import React from 'react';
import { Check } from 'lucide-react';

const SalesforceStageProgress = ({ stages, currentStage, className = '' }) => {
  const getStageStatus = (stageIndex) => {
    if (stageIndex < currentStage) return 'completed';
    if (stageIndex === currentStage) return 'current';
    return 'pending';
  };

  return (
    <div className={`sf-stage-progress ${className}`}>
      {stages.map((stage, index) => (
        <React.Fragment key={stage.id}>
          <div className={`sf-stage ${getStageStatus(index)}`}>
            {getStageStatus(index) === 'completed' ? (
              <Check className="w-4 h-4" />
            ) : (
              <span className="w-4 h-4 rounded-full border-2 border-current"></span>
            )}
            <span>{stage.label}</span>
          </div>
          
          {index < stages.length - 1 && (
            <div className={`sf-stage-connector ${getStageStatus(index) === 'completed' ? 'completed' : ''}`}></div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

export default SalesforceStageProgress;
