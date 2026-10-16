import Foundation
import AVFoundation
import ImageIO
import CoreGraphics
import CoreVideo

// Conversión local con el codificador del sistema. Conserva los cuadros y tiempos del GIF.
let input = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2])
guard let source = CGImageSourceCreateWithURL(input as CFURL, nil),
      let first = CGImageSourceCreateImageAtIndex(source, 0, nil) else { fatalError("GIF inválido") }
let width = (first.width / 2) * 2
let height = (first.height / 2) * 2
let writer = try AVAssetWriter(outputURL: output, fileType: .mp4)
let video = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: width, AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 2000000]
])
video.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: video,
    sourcePixelBufferAttributes: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
                                 kCVPixelBufferWidthKey as String: width, kCVPixelBufferHeightKey as String: height])
writer.add(video)
guard writer.startWriting() else { fatalError("No se pudo iniciar video: \(String(describing: writer.error))") }
writer.startSession(atSourceTime: .zero)
var time = 0.0
for i in 0..<CGImageSourceGetCount(source) {
    while !video.isReadyForMoreMediaData {
        if writer.status == .failed { fatalError("Codificación falló: \(String(describing: writer.error))") }
        Thread.sleep(forTimeInterval: 0.005)
    }
    guard let image = CGImageSourceCreateImageAtIndex(source, i, nil) else { fatalError("Cuadro inválido") }
    var optional: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &optional)
    let buffer = optional!
    CVPixelBufferLockBaseAddress(buffer, [])
    let context = CGContext(data: CVPixelBufferGetBaseAddress(buffer), width: width, height: height,
        bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(buffer), space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
    context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
    CVPixelBufferUnlockBaseAddress(buffer, [])
    guard adaptor.append(buffer, withPresentationTime: CMTime(seconds: time, preferredTimescale: 600)) else {
        fatalError("No se pudo escribir cuadro: \(String(describing: writer.error))")
    }
    let properties = CGImageSourceCopyPropertiesAtIndex(source, i, nil) as? [CFString: Any]
    let gif = properties?[kCGImagePropertyGIFDictionary] as? [CFString: Any]
    time += max(0.01, gif?[kCGImagePropertyGIFUnclampedDelayTime] as? Double ?? gif?[kCGImagePropertyGIFDelayTime] as? Double ?? 0.04)
}
writer.endSession(atSourceTime: CMTime(seconds: time, preferredTimescale: 600))
video.markAsFinished()
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
guard writer.status == .completed else { fatalError("Video incompleto: \(String(describing: writer.error))") }
print("\(output.lastPathComponent): \(width)x\(height), \(time) s")
