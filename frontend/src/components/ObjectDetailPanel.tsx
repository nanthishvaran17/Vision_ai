import React from 'react';
import { DetectedObject } from '../lib/types';
import { X, Box, Tag, Layers, MessageSquarePlus } from 'lucide-react';

interface ObjectDetailPanelProps {
  object: DetectedObject | null;
  onClose: () => void;
  onAskAboutObject: (label: string) => void;
}

export const ObjectDetailPanel: React.FC<ObjectDetailPanelProps> = ({
  object,
  onClose,
  onAskAboutObject
}) => {
  if (!object) return null;

  const colorAttr = object.attributes?.color || 'Neutral';
  const areaAttr = object.attributes?.area_percentage ? `${object.attributes.area_percentage}%` : 'N/A';

  return (
    <div className="fixed right-4 top-20 z-40 w-80 rounded-2xl border border-blue-500/30 bg-slate-900/95 p-5 shadow-2xl backdrop-blur-xl animate-in slide-in-from-right duration-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2 text-blue-400">
          <Box className="h-5 w-5" />
          <h3 className="font-semibold text-white capitalize">{object.label}</h3>
        </div>
        <button onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-4 space-y-3 text-sm">
        <div className="flex justify-between rounded-lg bg-slate-800/60 p-2.5">
          <span className="text-slate-400">Confidence Score:</span>
          <span className="font-mono font-semibold text-emerald-400">
            {Math.round(object.confidence * 100)}%
          </span>
        </div>

        <div className="flex justify-between rounded-lg bg-slate-800/60 p-2.5">
          <span className="text-slate-400">Detected Color:</span>
          <span className="font-medium text-slate-200 capitalize">{colorAttr}</span>
        </div>

        <div className="flex justify-between rounded-lg bg-slate-800/60 p-2.5">
          <span className="text-slate-400">Frame Coverage:</span>
          <span className="font-mono font-medium text-slate-200">{areaAttr}</span>
        </div>

        <div className="rounded-lg bg-slate-800/60 p-2.5">
          <span className="text-xs text-slate-400">Normalized Bounds [x1, y1, x2, y2]:</span>
          <div className="mt-1 font-mono text-xs text-blue-300">
            [{object.box.x1}, {object.box.y1}, {object.box.x2}, {object.box.y2}]
          </div>
        </div>
      </div>

      <button
        onClick={() => {
          onAskAboutObject(object.label);
          onClose();
        }}
        className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 font-medium text-white shadow-lg hover:bg-blue-500 active:scale-95 transition-all"
      >
        <MessageSquarePlus className="h-4 w-4" />
        Ask about this object
      </button>
    </div>
  );
};
