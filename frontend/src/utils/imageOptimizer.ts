/**
 * Image Optimization Utility for Low-Bandwidth Farms.
 * Resizes photos, compresses quality (<500KB), strips EXIF, and hashes payload.
 */

export interface OptimizedImageResult {
  blob: Blob;
  dataUrl: string;
  hash: string;
  originalSizeBytes: number;
  compressedSizeBytes: number;
}

export async function compressAndStripEXIF(
  file: File, 
  maxWidth = 1024, 
  maxHeight = 1024, 
  quality = 0.7
): Promise<OptimizedImageResult> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target?.result as string;

      img.onload = async () => {
        // Calculate new dimensions keeping aspect ratio
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > maxWidth) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = Math.round((width * maxHeight) / height);
            height = maxHeight;
          }
        }

        // Draw onto clean canvas (stripping EXIF metadata automatically)
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Canvas context unavailable'));
          return;
        }

        ctx.drawImage(img, 0, 0, width, height);

        // Convert canvas to compressed JPEG blob
        canvas.toBlob(
          async (blob) => {
            if (!blob) {
              reject(new Error('Image compression failed'));
              return;
            }

            const dataUrl = canvas.toDataURL('image/jpeg', quality);
            const arrayBuffer = await blob.arrayBuffer();
            
            // Simple SHA-256 hash generation
            const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');

            resolve({
              blob,
              dataUrl,
              hash: hashHex,
              originalSizeBytes: file.size,
              compressedSizeBytes: blob.size,
            });
          },
          'image/jpeg',
          quality
        );
      };

      img.onerror = () => reject(new Error('Failed to load image file'));
    };

    reader.onerror = () => reject(new Error('Failed to read file'));
  });
}
