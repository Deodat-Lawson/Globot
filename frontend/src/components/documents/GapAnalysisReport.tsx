import * as React from 'react';
import { cn } from '../ui/utils';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import type { DocumentSummary, MissingDocument, Recommendation } from '../../services/documentApi';

interface GapAnalysisReportProps {
  overallStatus: string;
  complianceScore: number;
  validDocuments: DocumentSummary[];
  expiringDocuments: DocumentSummary[];
  expiredDocuments: DocumentSummary[];
  missingDocuments: MissingDocument[];
  recommendations: Recommendation[];
  className?: string;
}

const STATUS_CONFIG = {
  COMPLIANT: {
    color: 'bg-green-500',
    textColor: 'text-green-700',
    bgColor: 'bg-green-50',
    label: 'Compliant'
  },
  PARTIAL: {
    color: 'bg-yellow-500',
    textColor: 'text-yellow-700',
    bgColor: 'bg-yellow-50',
    label: 'Partially Compliant'
  },
  NON_COMPLIANT: {
    color: 'bg-red-500',
    textColor: 'text-red-700',
    bgColor: 'bg-red-50',
    label: 'Non-Compliant'
  },
  ERROR: {
    color: 'bg-gray-500',
    textColor: 'text-gray-700',
    bgColor: 'bg-gray-50',
    label: 'Error'
  },
  PENDING_REVIEW: {
    color: 'bg-blue-500',
    textColor: 'text-blue-700',
    bgColor: 'bg-blue-50',
    label: 'Pending Review'
  }
};

const PRIORITY_BADGE_COLORS = {
  CRITICAL: 'bg-red-100 text-red-800 border-red-200',
  HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
  MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200'
};

function ComplianceGauge({ score, status }: { score: number; status: string }) {
  const config = STATUS_CONFIG[status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.PENDING_REVIEW;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="12"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            fill="none"
            stroke="currentColor"
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={`${(score / 100) * 352} 352`}
            className={config.textColor}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold">{score}</span>
          <span className="text-xs text-gray-500">/ 100</span>
        </div>
      </div>
      <Badge className={cn('mt-2', config.bgColor, config.textColor, 'border')}>
        {config.label}
      </Badge>
    </div>
  );
}

function DocumentList({
  title,
  documents,
  type
}: {
  title: string;
  documents: DocumentSummary[];
  type: 'valid' | 'expiring' | 'expired';
}) {
  if (documents.length === 0) return null;

  const icons = {
    valid: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-600">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
    ),
    expiring: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-yellow-600">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
    ),
    expired: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-600">
        <circle cx="12" cy="12" r="10" />
        <line x1="15" y1="9" x2="9" y2="15" />
        <line x1="9" y1="9" x2="15" y2="15" />
      </svg>
    )
  };

  const colors = {
    valid: 'border-green-200 bg-green-50',
    expiring: 'border-yellow-200 bg-yellow-50',
    expired: 'border-red-200 bg-red-50'
  };

  return (
    <div>
      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
        {icons[type]}
        {title} ({documents.length})
      </h4>
      <div className="space-y-2">
        {documents.map((doc, index) => (
          <div
            key={index}
            className={cn('p-2 rounded-lg border text-sm', colors[type])}
          >
            <div className="flex justify-between items-start">
              <span className="font-medium">
                {doc.document_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
              {doc.days_until_expiry !== null && doc.days_until_expiry !== undefined && (
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded',
                  doc.days_until_expiry < 0 ? 'bg-red-200 text-red-800' :
                  doc.days_until_expiry <= 30 ? 'bg-yellow-200 text-yellow-800' :
                  'bg-green-200 text-green-800'
                )}>
                  {doc.days_until_expiry < 0
                    ? `Expired ${Math.abs(doc.days_until_expiry)} days ago`
                    : `${doc.days_until_expiry} days`}
                </span>
              )}
            </div>
            {doc.expiry_date && (
              <p className="text-xs text-gray-500 mt-1">
                Expires: {doc.expiry_date}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function MissingDocumentsList({ documents }: { documents: MissingDocument[] }) {
  if (documents.length === 0) return null;

  return (
    <div>
      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-orange-600">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        Missing Documents ({documents.length})
      </h4>
      <div className="space-y-2">
        {documents.map((doc, index) => (
          <div
            key={index}
            className="p-2 rounded-lg border border-orange-200 bg-orange-50 text-sm"
          >
            <div className="flex justify-between items-start">
              <span className="font-medium">
                {doc.document_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
              <Badge className={cn('text-xs', PRIORITY_BADGE_COLORS[doc.priority])}>
                {doc.priority}
              </Badge>
            </div>
            {doc.required_by.length > 0 && (
              <p className="text-xs text-gray-500 mt-1">
                Required by: {doc.required_by.join(', ')}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function RecommendationsList({ recommendations }: { recommendations: Recommendation[] }) {
  if (recommendations.length === 0) return null;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
          Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {recommendations.map((rec, index) => (
          <div
            key={index}
            className={cn(
              'p-3 rounded-lg border',
              rec.priority === 'CRITICAL' ? 'border-red-200 bg-red-50' :
              rec.priority === 'HIGH' ? 'border-orange-200 bg-orange-50' :
              'border-yellow-200 bg-yellow-50'
            )}
          >
            <div className="flex items-start gap-2">
              <Badge className={cn('text-xs flex-shrink-0', PRIORITY_BADGE_COLORS[rec.priority])}>
                {rec.priority}
              </Badge>
              <div className="flex-1">
                <p className="text-sm font-medium">{rec.action}</p>
                {rec.documents.length > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    Documents: {rec.documents.join(', ')}
                  </p>
                )}
                {rec.deadline && (
                  <p className="text-xs text-gray-500 mt-0.5">
                    Deadline: {rec.deadline}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export function GapAnalysisReport({
  overallStatus,
  complianceScore,
  validDocuments,
  expiringDocuments,
  expiredDocuments,
  missingDocuments,
  recommendations,
  className
}: GapAnalysisReportProps) {
  const totalIssues = expiringDocuments.length + expiredDocuments.length + missingDocuments.length;

  return (
    <div className={cn('space-y-4', className)}>
      {/* Summary Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">Compliance Analysis Results</CardTitle>
          <CardDescription>
            {validDocuments.length} valid, {totalIssues} issues found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row items-center gap-6">
            <ComplianceGauge score={complianceScore} status={overallStatus} />
            <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{validDocuments.length}</div>
                <div className="text-xs text-gray-500">Valid</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{expiringDocuments.length}</div>
                <div className="text-xs text-gray-500">Expiring Soon</div>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{expiredDocuments.length}</div>
                <div className="text-xs text-gray-500">Expired</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{missingDocuments.length}</div>
                <div className="text-xs text-gray-500">Missing</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Document Details */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Document Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <DocumentList
            title="Valid Documents"
            documents={validDocuments}
            type="valid"
          />
          <DocumentList
            title="Expiring Soon"
            documents={expiringDocuments}
            type="expiring"
          />
          <DocumentList
            title="Expired Documents"
            documents={expiredDocuments}
            type="expired"
          />
          <MissingDocumentsList documents={missingDocuments} />
        </CardContent>
      </Card>

      {/* Recommendations */}
      <RecommendationsList recommendations={recommendations} />
    </div>
  );
}

export default GapAnalysisReport;
