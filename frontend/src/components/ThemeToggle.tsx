import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '', showLabel = false }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      type="button"
      aria-label="Toggle Theme"
      className={`relative inline-flex items-center gap-2 rounded-full px-3 py-1.5 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500/50 cursor-pointer ${
        theme === 'dark'
          ? 'bg-slate-800 text-amber-400 border border-slate-700 hover:bg-slate-750 hover:border-amber-400/50 shadow-lg'
          : 'bg-slate-200 text-indigo-700 border border-slate-300 hover:bg-slate-300 hover:border-indigo-500/50 shadow-md'
      } ${className}`}
    >
      {theme === 'dark' ? (
        <>
          <Moon className="h-4 w-4 text-amber-400 fill-amber-400/20 transform transition-transform duration-500" />
          <span className="text-xs font-bold tracking-wide text-slate-200 select-none">
            Dark Mode
          </span>
        </>
      ) : (
        <>
          <Sun className="h-4 w-4 text-amber-500 fill-amber-500/20 transform transition-transform duration-500" />
          <span className="text-xs font-bold tracking-wide text-slate-800 select-none">
            Light Mode
          </span>
        </>
      )}
    </button>
  );
};
