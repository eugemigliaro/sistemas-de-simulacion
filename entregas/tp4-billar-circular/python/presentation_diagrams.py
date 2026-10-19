"""Diagramas del motor, con una geometría compartida entre PDF y PPTX editable."""
import xml.etree.ElementTree as ET

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
BLUE = '005B91'


def box(text, x, y, w, h, kind='rect', size=27):
    return dict(text=text, x=x, y=y, w=w, h=h, kind=kind, size=size)


DIAGRAMS = {
    5: dict(nodes=[
        box('Configuración\nConfig', 480, 150, 320, 70, size=24),
        box('Inicialización\ngenerate()', 70, 315, 280, 70, size=24),
        box('Integración con Verlet\nsimulate()', 480, 315, 320, 70, size=24),
        box('Fuerzas de contacto\nforces()', 930, 315, 280, 70, size=24),
        box('Partícula\nParticle', 250, 490, 300, 70, size=24),
        box('Resultado de fuerzas\nForceResult', 730, 490, 300, 70, size=24),
        box('Vector 2D\nVec', 490, 615, 300, 65, size=24),
        box('Flecha discontinua: dependencia\nRombo: composición', 35, 155, 390, 90, 'label', 21),
        box('usa', 650, 249, 80, 34, 'label', 22),
        box('llama', 800, 306, 130, 34, 'label', 22),
        box('crea', 115, 431, 80, 34, 'label', 22),
        box('actualiza', 390, 405, 140, 34, 'label', 22),
        box('usa', 760, 405, 80, 34, 'label', 22),
        box('devuelve', 1080, 431, 150, 34, 'label', 22),
        box('contiene', 267, 573, 130, 34, 'label', 22),
        box('contiene', 885, 573, 130, 34, 'label', 22),
    ], edges=[
        ([(640, 315), (640, 220)], 'dependency'),
        ([(800, 350), (930, 350)], 'dependency'),
        ([(210, 385), (210, 525), (250, 525)], 'dependency'),
        ([(560, 385), (560, 445), (400, 445), (400, 490)], 'dependency'),
        ([(720, 385), (720, 445), (880, 445), (880, 490)], 'dependency'),
        ([(1070, 385), (1070, 525), (1030, 525)], 'dependency'),
        ([(400, 560), (400, 647), (490, 647)], 'composition'),
        ([(880, 560), (880, 647), (790, 647)], 'composition'),
    ]),
    6: dict(nodes=[
        box('Inicializar sin solapamientos\nr₀, v₀ y r₋₁', 90, 155, 565, 66, size=24),
        box('Fuerzas por contactos\nRegistrar la primera conversión', 90, 253, 565, 66, size=24),
        box('Verlet: posición y velocidad', 90, 351, 565, 58, size=24),
        box('Guardar estado cada n pasos', 90, 441, 565, 58, size=24),
        box('¿t = t final?', 248, 539, 250, 100, 'diamond', 23),
        box('Fin', 880, 560, 240, 58, 'roundRect', 25),
        box('Avanzar\nun paso', 65, 560, 165, 58, size=22),
        box('No', 190, 520, 70, 35, 'label', 22),
        box('Sí', 680, 550, 80, 38, 'label', 23),
        box('Grilla de celdas de ancho 2r\nImagen de pared en cada paso', 740, 175, 490, 100, 'label', 24),
        box('rₙ₊₁ = 2rₙ − rₙ₋₁ + h²Fₙ/m', 740, 325, 490, 60, 'label', 25),
        box('vₙ = (rₙ₊₁ − rₙ₋₁)/(2h)', 740, 395, 490, 60, 'label', 25),
    ], edges=[
        ([(373, 221), (373, 253)], 'arrow'),
        ([(373, 319), (373, 351)], 'arrow'),
        ([(373, 409), (373, 441)], 'arrow'),
        ([(373, 499), (373, 539)], 'arrow'),
        ([(498, 589), (880, 589)], 'arrow'),
        ([(248, 589), (230, 589)], 'arrow'),
        ([(65, 589), (40, 589), (40, 286), (90, 286)], 'arrow'),
    ]),
}


def tex_escape(text):
    replacements = {'r₀': '$\\mathbf r_0$', 'v₀': '$\\mathbf v_0$', 'r₋₁': '$\\mathbf r_{-1}$',
                    '2r': '$2r$', '¿t = t final?': '$t=t_f$?',
                    'rₙ₊₁ = 2rₙ − rₙ₋₁ + h²Fₙ/m': '$\\mathbf r_{n+1}=2\\mathbf r_n-\\mathbf r_{n-1}+h^2\\mathbf F_n/m$',
                    'vₙ = (rₙ₊₁ − rₙ₋₁)/(2h)': '$\\mathbf v_n=(\\mathbf r_{n+1}-\\mathbf r_{n-1})/(2h)$'}
    for source, target in sorted(replacements.items(), key=lambda item: -len(item[0])):
        text = text.replace(source, target)
    return text.replace('\n', r'\\')


def write_tex(path):
    lines = ['% Generado por presentation_diagrams.py. Coordenadas compartidas con PPTX.']
    for slide, diagram in DIAGRAMS.items():
        lines += [r'\expandafter\newcommand\csname diagram'+str(slide)+r'\endcsname{%',
                  r'\begin{tikzpicture}[remember picture,overlay,x=\paperwidth/1280,y=-\paperheight/720,>=Stealth]',
                  r'\begin{scope}[shift={(current page.north west)}]']
        for n in diagram['nodes']:
            x, y, w, h = (n[k] for k in ('x', 'y', 'w', 'h'))
            font = n['size'] * 455.244 / 1280
            style = f'font=\\fontsize{{{font:.3f}}}{{{font*1.2:.3f}}}\\selectfont,align=center,text=itbablue'
            if n['kind'] == 'package':
                lines += [f'\\draw[itbablue,thick] ({x},{y}) rectangle ({x+w},{y+h});',
                          f'\\node[{style},anchor=west] at ({x+25},{y+32}) '+'{'+n['text']+'};']
                continue
            if n['kind'] != 'label':
                if n['kind'] == 'diamond':
                    points = [(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)]
                    lines.append('\\draw[itbablue,thick,fill=softblue] '+' -- '.join(f'({a},{b})' for a,b in points)+' -- cycle;')
                else:
                    rounding = ',rounded corners=5pt' if n['kind']=='roundRect' else ''
                    lines.append(f'\\draw[itbablue,thick,fill=softblue{rounding}] ({x},{y}) rectangle ({x+w},{y+h});')
            lines.append(f'\\node[{style}] at ({x+w/2},{y+h/2}) {{{tex_escape(n["text"])}}};')
        for points, kind in diagram['edges']:
            options = '->,dashed' if kind == 'dependency' else '->' if kind == 'arrow' else ''
            lines.append('\\draw[itbablue,thick,'+options+'] '+' -- '.join(f'({x},{y})' for x,y in points)+';')
            if kind == 'composition':
                x,y=points[0]
                lines.append(f'\\fill[itbablue] ({x},{y}) -- ({x+6},{y+10}) -- ({x},{y+20}) -- ({x-6},{y+10}) -- cycle;')
        lines += [r'\end{scope}\end{tikzpicture}}']
    path.write_text('\n'.join(lines)+'\n')


def add_native(slide, number):
    """Agrega nodos, texto y conectores nativos sobre el fondo sin diagrama."""
    tree = slide.find(f'{{{P}}}cSld/{{{P}}}spTree')
    next_id = max(int(e.get('id', '0')) for e in slide.iter(f'{{{P}}}cNvPr')) + 1

    def element(parent, tag, **attrs):
        ns, local = tag.split(':')
        return ET.SubElement(parent, f'{{{P if ns == "p" else A}}}{local}', {k:str(v) for k,v in attrs.items()})

    def shape(n):
        nonlocal next_id
        sp=element(tree,'p:sp');nv=element(sp,'p:nvSpPr')
        element(nv,'p:cNvPr',id=next_id,name=n['text'].replace('\n',' '));next_id+=1
        element(nv,'p:cNvSpPr');element(nv,'p:nvPr')
        pr=element(sp,'p:spPr');tr=element(pr,'a:xfrm')
        element(tr,'a:off',x=round(n['x']*9525),y=round(n['y']*9525))
        element(tr,'a:ext',cx=round(n['w']*9525),cy=round(n['h']*9525))
        kind=n['kind'];geo='rect' if kind in ('label','package') else kind
        element(element(pr,'a:prstGeom',prst=geo),'a:avLst')
        if kind in ('label','package'):element(pr,'a:noFill')
        else:element(element(pr,'a:solidFill'),'a:srgbClr',val='E8F3F9')
        ln=element(pr,'a:ln',w=19050)
        if kind=='label':element(ln,'a:noFill')
        else:element(element(ln,'a:solidFill'),'a:srgbClr',val=BLUE)
        body=element(sp,'p:txBody');element(body,'a:bodyPr',anchor='t' if kind=='package' else 'ctr',lIns=100000,rIns=100000,tIns=60000,bIns=60000)
        element(body,'a:lstStyle')
        for text in n['text'].split('\n'):
            para=element(body,'a:p');element(para,'a:pPr',algn='l' if kind=='package' else 'ctr')
            run=element(para,'a:r');rp=element(run,'a:rPr',lang='es-AR',sz=round(n['size']*75))
            element(element(rp,'a:solidFill'),'a:srgbClr',val=BLUE);element(rp,'a:latin',typeface='Arial')
            element(run,'a:t').text=text

    for n in DIAGRAMS[number]['nodes']:shape(n)
    for points,kind in DIAGRAMS[number]['edges']:
        for i,((x,y),(xx,yy)) in enumerate(zip(points,points[1:])):
            sp=element(tree,'p:cxnSp');nv=element(sp,'p:nvCxnSpPr')
            element(nv,'p:cNvPr',id=next_id,name='Relación UML' if kind in ('composition','dependency') else 'Flujo');next_id+=1
            element(nv,'p:cNvCxnSpPr');element(nv,'p:nvPr');pr=element(sp,'p:spPr')
            tr=element(pr,'a:xfrm',**({'flipH':'1'} if xx<x else {}),**({'flipV':'1'} if yy<y else {}))
            element(tr,'a:off',x=round(min(x,xx)*9525),y=round(min(y,yy)*9525))
            element(tr,'a:ext',cx=round(abs(xx-x)*9525),cy=round(abs(yy-y)*9525))
            element(element(pr,'a:prstGeom',prst='line'),'a:avLst')
            ln=element(pr,'a:ln',w=19050);element(element(ln,'a:solidFill'),'a:srgbClr',val=BLUE)
            if kind=='dependency':element(ln,'a:prstDash',val='dash')
            if kind=='arrow' and i==len(points)-2:element(ln,'a:tailEnd',type='triangle',w='med',len='med')
            if kind=='dependency' and i==len(points)-2:element(ln,'a:tailEnd',type='arrow',w='med',len='med')
        if kind=='composition':
            x,y=points[0];shape(box('',x-6,y,12,20,'diamond'))
            # La composición UML usa un rombo relleno.
            fill=tree[-1].find(f'{{{P}}}spPr/{{{A}}}solidFill/{{{A}}}srgbClr');fill.set('val',BLUE)
