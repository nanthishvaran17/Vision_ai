import React, { useState } from 'react';
import { DetectedObject } from '../lib/types';
import { Eye, Info } from 'lucide-react';

interface VisualGroundingOverlayProps {
  imageSrc: string;
  objects: DetectedObject[];
  onSelectObject?: (obj: DetectedObject) => void;
  highlightedObjectId?: string | null;
}

export const VisualGroundingOverlay: React.FC<VisualGroundingOverlayProps> = ({
  imageSrc,
  objects,
  onSelectObject,
  highlightedObjectId
}) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="relative inline-block overflow-hidden rounded-xl border border-slate-700/60 bg-slate-900 group">
      <img
        src={imageSrc}
        alt="Analyzed visual target"
        className="block max-h-[480px] w-auto object-contain cursor-pointer"
        onClick={() => setIsModalOpen(true)}
      />

      {/* SVG Bounding Boxes Overlay */}
      <svg className="absolute inset-0 h-full w-full pointer-events-none" preserveAspectRatio="none">
        {objects.map((obj) => {
          const { x1, y1, x2, y2 } = obj.box;
          const left = `${x1 * 100}%`;
          const top = `${y1 * 100}%`;
          const width = `${(x2 - x1) * 100}%`;
          const height = `${(y2 - y1) * 100}%`;

          const isHighlighted = obj.id === highlightedObjectId || obj.id === hoveredId;

          return (
            <g key={obj.id} className="pointer-events-auto cursor-pointer" onClick={() => onSelectObject?.(obj)}>
              <rect
                x={left}
                y={top}
                width={width}
                height={height}
                fill={isHighlighted ? 'rgba(59, 130, 246, 0.25)' : 'rgba(59, 130, 246, 0.1)'}
                stroke={isHighlighted ? '#3b82f6' : '#60a5fa'}
                strokeWidth={isHighlighted ? '3' : '2'}
                strokeDasharray={isHighlighted ? 'none' : '4 2'}
                onMouseEnter={() => setHoveredId(obj.id)}
                onMouseLeave={() => setHoveredId(null)}
                className="transition-all duration-150"
              />
            </g>
          );
        })}
      </svg>

      {/* Interactive Labels Badges */}
      <div className="absolute inset-0 pointer-events-none">
        {objects.map((obj) => {
          const left = `${obj.box.x1 * 100}%`;
          const top = `${obj.box.y1 * 100}%`;
          const isHighlighted = obj.id === highlightedObjectId || obj.id === hoveredId;

          return (
            <div
              key={obj.id}
              style={{ left, top }}
              className="absolute pointer-events-auto transform -translate-y-full pb-1"
            >
              <button
                onClick={() => onSelectObject?.(obj)}
                onMouseEnter={() => setHoveredId(obj.id)}
                onMouseLeave={() => setHoveredId(null)}
                className={`flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium shadow-md transition-all ${
                  isHighlighted
                    ? 'bg-blue-600 text-white ring-2 ring-blue-300'
                    : 'bg-slate-900/90 text-blue-300 border border-blue-500/40 hover:bg-blue-900/80'
                }`}
              >
                <span>{obj.label}</span>
                <span className="opacity-75 font-mono">({Math.round(obj.confidence * 100)}%)</span>
              </button>
            </div>
          );
        })}
      </div>

      {/* Fullscreen Modal View */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4 backdrop-blur-md">
          <div className="relative max-h-[90vh] max-w-[90vw] overflow-auto rounded-2xl bg-slate-900 p-4 border border-slate-700">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute right-4 top-4 rounded-full bg-slate-800 p-2 text-slate-300 hover:bg-slate-700"
            >
              ✕
            </button>
            <div className="relative inline-block mt-8">
              <img src={imageSrc} alt="Full resolution" className="max-h-[80vh] w-auto rounded-lg" />
              <svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none">
                {objects.map((obj) => (
                  <rect
                    key={obj.id}
                    x={`${obj.box.x1 * 100}%`}
                    y={`${obj.box.y1 * 100}%`}
                    width={`${(obj.box.x2 - obj.box.x1) * 100}%`}
                    height={`${(obj.box.y2 - obj.box.y1) * 100}%`}
                    fill="rgba(59, 130, 246, 0.15)"
                    stroke="#3b82f6"
                    strokeWidth="2"
                  />
                ))}
              </svg>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
