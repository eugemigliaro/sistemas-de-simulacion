"""PDF Beamer y PPTX con videos, siguiendo la estructura del TP3 sin python-pptx.

LaTeX es la fuente editable. El PPTX mantiene el mecanismo previo: láminas
renderizadas y videos MP4 superpuestos sobre el fotograma. El runtime Artifact
Tool no está disponible en este host; se reutilizan los masters OOXML locales.
"""
import copy
import hashlib
import json
import posixpath
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'presentacion';BUILD=OUT/'.build';STEM='SdS_TP4_2026Q2G07CS_Presentacion'
REFERENCE=ROOT.parent/'tp3-billar-metegol/presentacion/SdS_TP3_2026Q2G07CS_Presentacion.pptx'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
ET.register_namespace('p',P);ET.register_namespace('a',A);ET.register_namespace('r',R)
ET.register_namespace('',CT)
WIDTH,HEIGHT=12192000,6858000
CLIPS={'energia':(255,0,255),'rendimiento':(0,255,255),'posicion':(255,255,0),
       'rapidez':(0,255,0),'densidad':(255,0,0)}


def xml(element):return ET.tostring(element,encoding='utf-8',xml_declaration=True)


def relationships(entries):
    root=ET.Element('Relationships',xmlns=REL)
    for ident,kind,target in entries:
        ET.SubElement(root,'Relationship',Id=ident,Type=kind if kind.startswith('http') else R+'/'+kind,Target=target)
    return xml(root)


def render(pdf,folder):
    folder.mkdir(parents=True,exist_ok=True)
    subprocess.run(['pdftoppm','-png','-scale-to-x','1920','-scale-to-y','1080',str(pdf),str(folder/'slide')],check=True)
    return sorted(folder.glob('slide-*.png'))


def main():
    BUILD.mkdir(exist_ok=True)
    links=json.loads((OUT/'enlaces.json').read_text())
    definitions=[]
    for name in CLIPS:
        url=links.get(name)
        if url and not re.fullmatch(r'https://(?:www\.)?(?:youtube\.com|youtu\.be|vimeo\.com)/[^\s{}%\\]+',url):
            raise ValueError('URL publica invalida: '+name)
        text=r'\url{'+url+'}' if url else 'YouTube/Vimeo: enlace pendiente de publicación'
        definitions.append(r'\expandafter\newcommand\csname enlace'+name+r'\endcsname{{\scriptsize\color{accent}'+text+'}}')
    (OUT/'enlaces.tex').write_text('\n'.join(definitions)+'\n')
    subprocess.run(['/opt/homebrew/bin/tectonic','--only-cached','--keep-logs',STEM+'.tex'],cwd=OUT,check=True,capture_output=True,text=True)
    pages=render(OUT/(STEM+'.pdf'),BUILD/'paginas')
    official_pdf=OUT/'SdS_TP4_2026Q2G07CS_Presentación.pdf'
    shutil.copy2(OUT/(STEM+'.pdf'),official_pdf)

    # Encontrar las cajas de videos con el mismo procedimiento visual del TP3.
    mask=BUILD/'mascara';(mask/'figuras').mkdir(parents=True,exist_ok=True)
    shutil.copy2(OUT/(STEM+'.tex'),mask/(STEM+'.tex'));shutil.copy2(OUT/'enlaces.tex',mask/'enlaces.tex')
    for path in (OUT/'figuras').iterdir():
        dest=mask/'figuras'/path.name
        matching=next((n for n in CLIPS if path.name==f'anim-{n}.png'),None)
        if matching:
            with Image.open(path) as im:Image.new('RGB',im.size,CLIPS[matching]).save(dest)
        elif not dest.exists():dest.symlink_to(path)
    subprocess.run(['/opt/homebrew/bin/tectonic','--only-cached',STEM+'.tex'],cwd=mask,check=True,capture_output=True,text=True)
    marked=render(mask/(STEM+'.pdf'),BUILD/'mascara-paginas');boxes={}
    for i,path in enumerate(marked):
        arr=np.array(Image.open(path).convert('RGB')).astype(int)
        for name,color in CLIPS.items():
            hit=np.all(np.abs(arr-np.array(color))<3,axis=2)
            if hit.sum()>10000:
                y,x=np.nonzero(hit);boxes[i]=(name,(x.min()/1920,y.min()/1080,(x.max()+1)/1920,(y.max()+1)/1080))
    if {n for n,_ in boxes.values()}!=set(CLIPS):raise ValueError('No se encontraron los cinco fotogramas')
    if len(pages)!=29:raise ValueError('Cantidad de laminas inesperada')
    timings=[(int(n),int(t)) for n,t in re.findall(r'^% (\d+) -- (\d+) s',(OUT/(STEM+'.tex')).read_text(),re.M)]
    if sum(t for _,t in timings)!=780:raise ValueError('El ensayo no suma 13 minutos')

    with zipfile.ZipFile(REFERENCE) as original:
        sample=ET.fromstring(original.read('ppt/slides/slide1.xml'))
        movie_slide=ET.fromstring(original.read('ppt/slides/slide17.xml'))
        movie_pic=movie_slide.find(f'{{{P}}}cSld/{{{P}}}spTree').findall(f'{{{P}}}pic')[1]
        presentation=ET.fromstring(original.read('ppt/presentation.xml'))
        ids=presentation.find(f'{{{P}}}sldIdLst');ids.clear()
        rels=[('rId1','slideMaster','slideMasters/slideMaster1.xml'),('rId2','presProps','presProps.xml'),
              ('rId3','viewProps','viewProps.xml'),('rId4','theme','theme/theme1.xml'),('rId5','tableStyles','tableStyles.xml')]
        contents=ET.fromstring(original.read('[Content_Types].xml'))
        for element in list(contents):
            part=element.get('PartName','')
            if part.startswith(('/ppt/slides/','/ppt/notesSlides/','/ppt/notesMasters/')):contents.remove(element)
        def override(part,kind):ET.SubElement(contents,f'{{{CT}}}Override',PartName='/'+part,ContentType=kind)
        for ext,kind in [('png','image/png'),('mp4','video/mp4')]:
            if not any(x.get('Extension')==ext for x in contents):ET.SubElement(contents,f'{{{CT}}}Default',Extension=ext,ContentType=kind)
        mime='application/vnd.openxmlformats-officedocument.presentationml.'
        target=OUT/(STEM+'.pptx')
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for name in original.namelist():
                if name.startswith(('ppt/slideMasters/','ppt/slideLayouts/','ppt/theme/')) or name in ['ppt/presProps.xml','ppt/viewProps.xml','ppt/tableStyles.xml']:
                    z.writestr(name,original.read(name))
            for i,page in enumerate(pages):
                number=i+1;ident='rId'+str(7+i)
                ET.SubElement(ids,f'{{{P}}}sldId',id=str(256+i),**{f'{{{R}}}id':ident})
                rels.append((ident,'slide',f'slides/slide{number}.xml'))
                slide=copy.deepcopy(sample);sp=slide.find(f'{{{P}}}cSld/{{{P}}}spTree')
                pic=sp.find(f'{{{P}}}pic');pic.find(f'{{{P}}}nvPicPr/{{{P}}}cNvPr').set('descr',f'TP4 diapositiva {number}; fuente editable Beamer')
                relations=[('rId1','slideLayout','../slideLayouts/slideLayout7.xml'),
                           ('rId2','image',f'../media/slide{number}.png')]
                z.writestr(f'ppt/media/slide{number}.png',page.read_bytes())
                if i in boxes:
                    name,(x0,y0,x1,y1)=boxes[i];video=OUT/'videos'/(name+'-live.mp4')
                    if not video.exists() or video.stat().st_size<1000:raise ValueError('Falta video '+name)
                    media=copy.deepcopy(movie_pic);media.find(f'{{{P}}}nvPicPr/{{{P}}}cNvPr').set('name',name+'.mp4')
                    for click in media.iter(f'{{{A}}}hlinkClick'):
                        if click.get(f'{{{R}}}id')=='':del click.attrib[f'{{{R}}}id']
                    transform=media.find(f'{{{P}}}spPr/{{{A}}}xfrm')
                    transform.find(f'{{{A}}}off').attrib.update(x=str(round(x0*WIDTH)),y=str(round(y0*HEIGHT)))
                    transform.find(f'{{{A}}}ext').attrib.update(cx=str(round((x1-x0)*WIDTH)),cy=str(round((y1-y0)*HEIGHT)))
                    sp.append(media);slide.append(copy.deepcopy(movie_slide.find(f'{{{P}}}timing')))
                    relations.extend([('rId3','http://schemas.microsoft.com/office/2007/relationships/media',f'../media/{name}.mp4'),
                        ('rId4','video',f'../media/{name}.mp4'),('rId5','image',f'../media/{name}-poster.png')])
                    z.writestr(f'ppt/media/{name}.mp4',video.read_bytes());z.writestr(f'ppt/media/{name}-poster.png',(OUT/'figuras'/('anim-'+name+'.png')).read_bytes())
                z.writestr(f'ppt/slides/slide{number}.xml',xml(slide))
                z.writestr(f'ppt/slides/_rels/slide{number}.xml.rels',relationships(relations))
                override(f'ppt/slides/slide{number}.xml',mime+'slide+xml')
            z.writestr('ppt/presentation.xml',xml(presentation));z.writestr('ppt/_rels/presentation.xml.rels',relationships(rels))
            z.writestr('[Content_Types].xml',xml(contents))
            z.writestr('_rels/.rels',relationships([('rId1','officeDocument','ppt/presentation.xml'),
                ('rId2','http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties','docProps/core.xml'),
                ('rId3','extended-properties','docProps/app.xml')]))
            z.writestr('docProps/core.xml','''<?xml version="1.0" encoding="UTF-8"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>TP4 - Dinámica molecular por paso temporal</dc:title><dc:creator>Grupo 07 - Comisión S</dc:creator><dc:description>Borrador para revisión; asistencia de IA declarada en la última diapositiva.</dc:description></cp:coreProperties>''')
            z.writestr('docProps/app.xml',f'''<?xml version="1.0"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>LaTeX Beamer y ensamblado OOXML</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>{len(pages)}</Slides><Notes>0</Notes></Properties>''')
    # Keynote rechaza el master de notas anterior. El guion y las fuentes se
    # conservan en GUION.md y notas.json, fuera del paquete para exposición.
    # Resolver todos los vínculos internos del paquete y comprobar los videos.
    with zipfile.ZipFile(target) as z:
        names=set(z.namelist())
        for name in names:
            if name.endswith('.xml') or name.endswith('.rels'):ET.fromstring(z.read(name))
            if name.endswith('.rels'):
                base=posixpath.dirname(posixpath.dirname(name)) if name!='_rels/.rels' else ''
                for rel in ET.fromstring(z.read(name)):
                    if rel.get('TargetMode')=='External':continue
                    resolved=posixpath.normpath(posixpath.join(base,rel.get('Target')))
                    if resolved not in names:raise ValueError('Vinculo interno roto: '+resolved)
        assert len([n for n in names if n.endswith('.mp4')])==5
        assert not any(n.startswith(('ppt/notesSlides/','ppt/notesMasters/')) for n in names)
    report=dict(slides=len(pages),seconds=sum(t for _,t in timings),video_slides={str(i+1):name for i,(name,_) in boxes.items()},
        pending_public_links=[name for name,url in links.items() if not url],
        reference_sha256=hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
        outputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [target,official_pdf]},
        runtime_fallback='Artifact Tool no disponible; Beamer y masters OOXML del PPTX previo; fuente editable TeX')
    (BUILD/'presentation-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
