import React, { useState, useRef } from 'react';
import axiosInstance from '../../lib/axios';

interface UploadedImage {
  filename: string;
  url: string;
  thumbnail_url?: string;
  size: number;
  uploaded_at: string;
}

const Images: React.FC = () => {
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);

    try {
      const formData = new FormData();
      Array.from(files).forEach((file) => {
        formData.append('images', file);
      });

      const response = await axiosInstance.post('/api/images/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setImages([...response.data, ...images]);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload images');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (filename: string) => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      try {
        await axiosInstance.delete(`/api/images/${filename}`);
        setImages(images.filter((img) => img.filename !== filename));
      } catch (error) {
        console.error('Delete failed:', error);
        alert('Failed to delete image');
      }
    }
  };

  const copyToClipboard = (url: string) => {
    navigator.clipboard.writeText(url);
    alert('Image URL copied to clipboard!');
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Image Library</h1>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileSelect}
            className="hidden"
            id="image-upload"
          />
          <label
            htmlFor="image-upload"
            className={`px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 cursor-pointer ${
              isUploading ? 'opacity-50 pointer-events-none' : ''
            }`}
          >
            {isUploading ? 'Uploading...' : '+ Upload Images'}
          </label>
        </div>
      </div>

      {/* Upload Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          <strong>Supported formats:</strong> PNG, JPG, JPEG, GIF, WEBP
          <br />
          <strong>Max size:</strong> 16MB per image
          <br />
          <strong>Optimization:</strong> Images are automatically resized and optimized
        </p>
      </div>

      {/* Images Grid */}
      {images.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No images uploaded yet. Click "Upload Images" to start.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {images.map((image) => (
            <div
              key={image.filename}
              className="bg-white rounded-lg shadow overflow-hidden group relative"
            >
              <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                <img
                  src={image.thumbnail_url || image.url}
                  alt={image.filename}
                  className="w-full h-full object-cover cursor-pointer hover:scale-110 transition-transform"
                  onClick={() => setSelectedImage(image.url)}
                />
              </div>
              <div className="p-3">
                <p className="text-xs text-gray-600 truncate mb-1">{image.filename}</p>
                <p className="text-xs text-gray-400">
                  {(image.size / 1024).toFixed(1)} KB
                </p>
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => copyToClipboard(image.url)}
                    className="text-xs text-blue-600 hover:text-blue-900"
                  >
                    Copy URL
                  </button>
                  <button
                    onClick={() => handleDelete(image.filename)}
                    className="text-xs text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Image Preview Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
          onClick={() => setSelectedImage(null)}
        >
          <img
            src={selectedImage}
            alt="Preview"
            className="max-w-full max-h-full object-contain"
          />
        </div>
      )}
    </div>
  );
};

export default Images;
