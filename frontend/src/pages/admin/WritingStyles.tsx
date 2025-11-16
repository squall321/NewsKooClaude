import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { writingStylesApi } from '../../api/writingStyles';
import { WritingStyle } from '../../types';

const WritingStyles: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingStyle, setEditingStyle] = useState<WritingStyle | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tone: '',
    style_guide: '',
  });

  const queryClient = useQueryClient();

  const { data: styles, isLoading } = useQuery({
    queryKey: ['writing-styles'],
    queryFn: writingStylesApi.getStyles,
  });

  const createMutation = useMutation({
    mutationFn: writingStylesApi.createStyle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['writing-styles'] });
      setIsModalOpen(false);
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<WritingStyle> }) =>
      writingStylesApi.updateStyle(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['writing-styles'] });
      setIsModalOpen(false);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: writingStylesApi.deleteStyle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['writing-styles'] });
    },
  });

  const resetForm = () => {
    setFormData({ name: '', description: '', tone: '', style_guide: '' });
    setEditingStyle(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingStyle) {
      updateMutation.mutate({ id: editingStyle.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (style: WritingStyle) => {
    setEditingStyle(style);
    setFormData({
      name: style.name,
      description: style.description || '',
      tone: style.tone,
      style_guide: style.style_guide || '',
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this writing style?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return <div className="text-gray-600">Loading...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Writing Styles</h1>
        <button
          onClick={() => {
            resetForm();
            setIsModalOpen(true);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + New Style
        </button>
      </div>

      {/* Styles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {styles?.map((style) => (
          <div key={style.id} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-2">{style.name}</h3>
            <p className="text-gray-600 text-sm mb-3">{style.description}</p>
            <div className="mb-3">
              <span className="text-xs font-medium text-gray-500">Tone:</span>
              <span className="ml-2 text-sm text-gray-700">{style.tone}</span>
            </div>
            {style.style_guide && (
              <div className="mb-4">
                <span className="text-xs font-medium text-gray-500">Style Guide:</span>
                <p className="text-sm text-gray-700 mt-1 line-clamp-3">{style.style_guide}</p>
              </div>
            )}
            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(style)}
                className="px-3 py-1 text-sm text-blue-600 hover:text-blue-900"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(style.id)}
                className="px-3 py-1 text-sm text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
            <h2 className="text-2xl font-bold mb-4">
              {editingStyle ? 'Edit Style' : 'New Style'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tone</label>
                <input
                  type="text"
                  value={formData.tone}
                  onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
                  placeholder="e.g., casual, formal, humorous"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Style Guide
                </label>
                <textarea
                  value={formData.style_guide}
                  onChange={(e) => setFormData({ ...formData, style_guide: e.target.value })}
                  placeholder="Detailed writing style instructions for AI..."
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={6}
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false);
                    resetForm();
                  }}
                  className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  {editingStyle ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default WritingStyles;
