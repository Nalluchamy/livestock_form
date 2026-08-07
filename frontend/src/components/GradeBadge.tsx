import React from 'react';
import { GradeLevel } from '../types';

interface GradeBadgeProps {
  grade: GradeLevel;
  size?: 'sm' | 'md' | 'lg';
}

export const GradeBadge: React.FC<GradeBadgeProps> = ({ grade, size = 'md' }) => {
  const styles = {
    A: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    B: 'bg-teal-100 text-teal-800 border-teal-300',
    C: 'bg-amber-100 text-amber-800 border-amber-300',
    D: 'bg-rose-100 text-rose-800 border-rose-300',
  };

  const sizes = {
    sm: 'w-7 h-7 text-xs font-bold border',
    md: 'w-10 h-10 text-base font-extrabold border-2',
    lg: 'w-16 h-16 text-2xl font-black border-4',
  };

  return (
    <div
      className={`rounded-full flex items-center justify-center shadow-sm ${styles[grade]} ${sizes[size]}`}
    >
      Grade {grade}
    </div>
  );
};
