import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { AttributeForm, AttributeFormData } from '../components/AttributeForm';
import { ImageUploader } from '../components/ImageUploader';
import { submitGrade } from '../services/gradingService';
import { ErrorState } from '../components/ErrorState';

export const CaptureGrade: React.FC = () => {
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: submitGrade,
    onSuccess: (data) => {
      // Pass the result data state to the result page
      navigate('/result', { state: { result: data } });
    },
  });

  const handleSubmit = (formData: AttributeFormData) => {
    const { human_grade, ...attributes } = formData;
    mutation.mutate({
      attributes,
      human_grade: human_grade || undefined,
    });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 pb-20 md:pb-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        <div>
          <h2 className="text-xl font-bold text-civic-navy">Capture & Grade Livestock</h2>
          <p className="text-sm text-slate-500 mt-1">
            Input measured physical attributes to trigger the deterministic explainable rule engine.
          </p>
        </div>

        <ImageUploader />

        <hr className="border-slate-200" />

        <AttributeForm onSubmit={handleSubmit} isLoading={mutation.isPending} />

        {mutation.isError && (
          <ErrorState
            message={
              mutation.error instanceof Error
                ? mutation.error.message
                : 'Failed to evaluate livestock grade. Please check your backend connection.'
            }
          />
        )}
      </div>
    </div>
  );
};
