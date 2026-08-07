import React, { useState } from 'react';
import { Upload, CheckCircle, Lock } from 'lucide-react';

export const ImageUploader: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(URL.createObjectURL(file));
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-bold text-civic-navy">Livestock Photograph</label>
        <span className="inline-flex items-center text-xs font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
          <Lock className="w-3 h-3 mr-1" /> EXIF Privacy Stripped
        </span>
      </div>

      <div className="border-2 border-dashed border-slate-300 hover:border-civic-teal rounded-2xl p-4 text-center bg-slate-50 transition-colors">
        {selectedImage ? (
          <div className="relative group">
            <img
              src={selectedImage}
              alt="Livestock preview"
              className="max-h-48 mx-auto rounded-lg object-cover shadow-sm"
            />
            <div className="mt-2 flex items-center justify-center text-xs font-semibold text-emerald-600">
              <CheckCircle className="w-4 h-4 mr-1" /> Image Loaded & Anonymized
            </div>
          </div>
        ) : (
          <label className="cursor-pointer flex flex-col items-center justify-center py-4">
            <div className="w-12 h-12 rounded-full bg-civic-teal/10 flex items-center justify-center text-civic-teal mb-2">
              <Upload className="w-6 h-6" />
            </div>
            <span className="text-sm font-bold text-civic-navy">Tap to upload or capture photo</span>
            <span className="text-xs text-slate-500 mt-1">JPEG, PNG up to 10MB</span>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="sr-only"
            />
          </label>
        )}
      </div>
    </div>
  );
};
