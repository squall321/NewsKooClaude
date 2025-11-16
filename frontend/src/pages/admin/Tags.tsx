import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tagsApi } from '../../api/tags';
import type { Tag } from '../../types';

const Tags: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [tagName, setTagName] = useState('');

  const queryClient = useQueryClient();

  const { data: tags, isLoading } = useQuery({
    queryKey: ['tags'],
    queryFn: () => tagsApi.getTags(),
  });

  const createMutation = useMutation({
    mutationFn: tagsApi.createTag,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      setIsModalOpen(false);
      setTagName('');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Tag> }) =>
      tagsApi.updateTag(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      setIsModalOpen(false);
      setTagName('');
      setEditingTag(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: tagsApi.deleteTag,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingTag) {
      updateMutation.mutate({ id: editingTag.id, data: { name: tagName } });
    } else {
      createMutation.mutate({ name: tagName });
    }
  };

  const handleEdit = (tag: Tag) => {
    setEditingTag(tag);
    setTagName(tag.name);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this tag?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return <div className="text-gray-600">Loading...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Tags</h1>
        <button
          onClick={() => {
            setTagName('');
            setEditingTag(null);
            setIsModalOpen(true);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + New Tag
        </button>
      </div>

      {/* Tags Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
        {tags?.map((tag) => (
          <div
            key={tag.id}
            className="bg-white rounded-lg shadow p-4 flex flex-col items-center"
          >
            <div className="text-2xl mb-2">🏷️</div>
            <h3 className="text-sm font-medium text-gray-900 text-center mb-2">{tag.name}</h3>
            <div className="text-xs text-gray-500 mb-3">{tag.slug}</div>
            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(tag)}
                className="text-xs text-blue-600 hover:text-blue-900"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(tag.id)}
                className="text-xs text-red-600 hover:text-red-900"
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
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">{editingTag ? 'Edit Tag' : 'New Tag'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tag Name</label>
                <input
                  type="text"
                  value={tagName}
                  onChange={(e) => setTagName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false);
                    setTagName('');
                    setEditingTag(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  {editingTag ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tags;
