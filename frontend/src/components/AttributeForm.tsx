import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const attributeSchema = z.object({
  body_condition: z.coerce.number().min(1.0, 'BCS must be at least 1.0').max(5.0, 'BCS cannot exceed 5.0'),
  coat_quality: z.enum(['Smooth', 'Slightly rough', 'Rough', 'Severe lesions']),
  eye_condition: z.enum(['Clear', 'Slight discharge', 'Cloudy', 'Severe infection']),
  wound_presence: z.enum(['None', 'Minor', 'Moderate', 'Severe']),
  mobility: z.enum(['Normal', 'Slight limp', 'Lame', 'Unable to stand']),
  appetite: z.enum(['Good', 'Fair', 'Poor', 'None']),
  human_grade: z.enum(['A', 'B', 'C', 'D']).optional(),
});

export type AttributeFormData = z.infer<typeof attributeSchema>;

interface AttributeFormProps {
  onSubmit: (data: AttributeFormData) => void;
  isLoading: boolean;
}

export const AttributeForm: React.FC<AttributeFormProps> = ({ onSubmit, isLoading }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AttributeFormData>({
    resolver: zodResolver(attributeSchema),
    defaultValues: {
      body_condition: 3.0,
      coat_quality: 'Smooth',
      eye_condition: 'Clear',
      wound_presence: 'None',
      mobility: 'Normal',
      appetite: 'Good',
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Body Condition Score Slider */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="text-sm font-bold text-civic-navy">
            Body Condition Score (BCS) <span className="text-rose-500">*</span>
          </label>
          <span className="text-xs font-semibold px-2 py-1 bg-civic-teal/10 text-civic-teal rounded">
            Scale 1.0 (Emaciated) - 5.0 (Obese)
          </span>
        </div>
        <input
          type="number"
          step="0.1"
          min="1.0"
          max="5.0"
          {...register('body_condition')}
          className="w-full h-12 px-4 rounded-xl border border-slate-300 font-semibold text-lg focus:ring-2 focus:ring-civic-teal focus:outline-none"
        />
        {errors.body_condition && (
          <p className="text-xs font-bold text-rose-500">{errors.body_condition.message}</p>
        )}
      </div>

      {/* Grid of Dropdowns for mobile accessibility */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Coat Quality */}
        <div className="space-y-1.5">
          <label className="text-sm font-bold text-civic-navy">Coat Quality</label>
          <select
            {...register('coat_quality')}
            className="w-full h-12 px-3 rounded-xl border border-slate-300 font-medium bg-white focus:ring-2 focus:ring-civic-teal focus:outline-none"
          >
            <option value="Smooth">Smooth (Grade A)</option>
            <option value="Slightly rough">Slightly Rough (Grade B)</option>
            <option value="Rough">Rough (Grade C)</option>
            <option value="Severe lesions">Severe Lesions (Grade D)</option>
          </select>
        </div>

        {/* Eye Condition */}
        <div className="space-y-1.5">
          <label className="text-sm font-bold text-civic-navy">Eye Condition</label>
          <select
            {...register('eye_condition')}
            className="w-full h-12 px-3 rounded-xl border border-slate-300 font-medium bg-white focus:ring-2 focus:ring-civic-teal focus:outline-none"
          >
            <option value="Clear">Clear & Bright (Grade A)</option>
            <option value="Slight discharge">Slight Discharge (Grade B)</option>
            <option value="Cloudy">Cloudy / Tearing (Grade C)</option>
            <option value="Severe infection">Severe Infection (Grade D)</option>
          </select>
        </div>

        {/* Wound Presence */}
        <div className="space-y-1.5">
          <label className="text-sm font-bold text-civic-navy">Wound / Injuries</label>
          <select
            {...register('wound_presence')}
            className="w-full h-12 px-3 rounded-xl border border-slate-300 font-medium bg-white focus:ring-2 focus:ring-civic-teal focus:outline-none"
          >
            <option value="None">None (Grade A)</option>
            <option value="Minor">Minor Scratches (Grade B)</option>
            <option value="Moderate">Moderate Wounds (Grade C)</option>
            <option value="Severe">Severe / Infected (Grade D)</option>
          </select>
        </div>

        {/* Mobility */}
        <div className="space-y-1.5">
          <label className="text-sm font-bold text-civic-navy">Mobility</label>
          <select
            {...register('mobility')}
            className="w-full h-12 px-3 rounded-xl border border-slate-300 font-medium bg-white focus:ring-2 focus:ring-civic-teal focus:outline-none"
          >
            <option value="Normal">Normal Gait (Grade A)</option>
            <option value="Slight limp">Slight Limp (Grade B)</option>
            <option value="Lame">Lame (Grade C)</option>
            <option value="Unable to stand">Unable to Stand (Grade D)</option>
          </select>
        </div>

        {/* Appetite */}
        <div className="space-y-1.5 sm:col-span-2">
          <label className="text-sm font-bold text-civic-navy">Appetite</label>
          <select
            {...register('appetite')}
            className="w-full h-12 px-3 rounded-xl border border-slate-300 font-medium bg-white focus:ring-2 focus:ring-civic-teal focus:outline-none"
          >
            <option value="Good">Good (Grade A)</option>
            <option value="Fair">Fair (Grade B)</option>
            <option value="Poor">Poor (Grade C)</option>
            <option value="None">None / Lethargic (Grade D)</option>
          </select>
        </div>
      </div>

      {/* Human Grader Initial Assessment */}
      <div className="p-4 bg-slate-100 rounded-xl border border-slate-200 space-y-2">
        <label className="text-sm font-bold text-civic-navy block">
          Human Expert Grade (Optional Comparison)
        </label>
        <p className="text-xs text-slate-500">
          Enter your manual grade to test disagreement detection against the AI system.
        </p>
        <div className="flex space-x-3 pt-1">
          {['A', 'B', 'C', 'D'].map((g) => (
            <label
              key={g}
              className="flex-1 border rounded-lg p-2.5 text-center font-extrabold cursor-pointer hover:bg-white transition-colors has-[:checked]:bg-civic-teal has-[:checked]:text-white has-[:checked]:border-civic-teal"
            >
              <input
                type="radio"
                value={g}
                {...register('human_grade')}
                className="sr-only"
              />
              Grade {g}
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full h-14 bg-civic-teal hover:bg-civic-lightTeal text-white font-bold text-lg rounded-xl shadow-md flex items-center justify-center space-x-2 transition-transform active:scale-[0.99] disabled:opacity-50"
      >
        {isLoading ? (
          <span>Calculating Grade...</span>
        ) : (
          <span>Calculate Explainable Grade</span>
        )}
      </button>
    </form>
  );
};
