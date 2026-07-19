import React, { useMemo, useState } from 'react';
import { Card, KpiCard, ChartContainer, DataTable, LoadingSkeleton, EmptyState, AlertBanner, Modal, Badge } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { useRiskPredictions, useRiskSummary, useDistrictRisk, useStationRisk } from 'features/risk-scoring/hooks/useRiskScoring';
import type { RiskPrediction, DistrictRisk, StationRisk } from 'features/risk-scoring/hooks/useRiskScoring';

const RISK_LEVEL_VARIANT: Record<string, 'success' | 'warning' | 'danger'> = {
  LOW: 'success',
  MEDIUM: 'warning',
  HIGH: 'danger',
  CRITICAL: 'danger',
};

const RiskScoring: React.FC = () => {
  const [selectedEntity, setSelectedEntity] = useState<RiskPrediction | null>(null);
  const { data: predictions, isLoading: predictionsLoading, error: predictionsError } = useRiskPredictions(100);
  const { data: summary, isLoading: summaryLoading } = useRiskSummary();
  const { data: districtRisk, isLoading: districtLoading } = useDistrictRisk();
  const { data: stationRisk, isLoading: stationLoading } = useStationRisk();

  const districtChartData = useMemo(
    () =>
      (districtRisk ?? []).map((d) => ({
        district: d.district_name,
        score: d.risk_score,
      })),
    [districtRisk]
  );

  const stationChartData = useMemo(
    () =>
      (stationRisk ?? []).map((s) => ({
        station: s.station_name,
        score: s.risk_score,
      })),
    [stationRisk]
  );

  const predictionColumns: DataTableColumn<RiskPrediction>[] = [
    { key: 'entity_name', header: 'Name', render: (r) => r.entity_name },
    { key: 'entity_type', header: 'Type', render: (r) => r.entity_type },
    {
      key: 'risk_level',
      header: 'Level',
      render: (r) => <Badge variant={RISK_LEVEL_VARIANT[r.risk_level] ?? 'secondary'}>{r.risk_level}</Badge>,
    },
    {
      key: 'risk_score',
      header: 'Score',
      sortable: true,
      sortValue: (r) => r.risk_score,
      render: (r) => r.risk_score.toFixed(1),
    },
    {
      key: 'last_updated',
      header: 'Updated',
      render: (r) => (r.last_updated ? new Date(r.last_updated).toLocaleDateString() : '-'),
    },
  ];

  const districtColumns: DataTableColumn<DistrictRisk>[] = [
    { key: 'district_name', header: 'District', render: (r) => r.district_name },
    { key: 'crime_count', header: 'Crimes', render: (r) => r.crime_count },
    { key: 'fir_count', header: 'FIRs', render: (r) => r.fir_count },
    {
      key: 'risk_level',
      header: 'Level',
      render: (r) => <Badge variant={RISK_LEVEL_VARIANT[r.risk_level] ?? 'secondary'}>{r.risk_level}</Badge>,
    },
    {
      key: 'risk_score',
      header: 'Score',
      sortable: true,
      sortValue: (r) => r.risk_score,
      render: (r) => r.risk_score.toFixed(1),
    },
  ];

  const stationColumns: DataTableColumn<StationRisk>[] = [
    { key: 'station_name', header: 'Station', render: (r) => r.station_name },
    { key: 'district_name', header: 'District', render: (r) => r.district_name },
    { key: 'crime_count', header: 'Crimes', render: (r) => r.crime_count },
    { key: 'fir_count', header: 'FIRs', render: (r) => r.fir_count },
    {
      key: 'risk_level',
      header: 'Level',
      render: (r) => <Badge variant={RISK_LEVEL_VARIANT[r.risk_level] ?? 'secondary'}>{r.risk_level}</Badge>,
    },
    {
      key: 'risk_score',
      header: 'Score',
      sortable: true,
      sortValue: (r) => r.risk_score,
      render: (r) => r.risk_score.toFixed(1),
    },
  ];

  if (predictionsError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Risk Scoring</h1>
          <p className="text-sm text-gov-slate">Composite risk indices by district, station, and entity</p>
        </div>
        <AlertBanner variant="error" title="Failed to load risk data" message="Unable to fetch risk predictions. Please try again later." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Risk Scoring</h1>
        <p className="text-sm text-gov-slate">Composite risk indices by district, station, and entity</p>
      </div>

      {summaryLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-5">
              <LoadingSkeleton variant="card" />
            </Card>
          ))}
        </div>
      ) : summary ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Average Risk Score" value={summary.average_risk.toFixed(1)} accent="amber" />
          <KpiCard label="High Risk Districts" value={summary.total_high_risk} accent="red" />
          <KpiCard label="Critical Entities" value={summary.total_critical_risk} accent="red" />
          <KpiCard label="Total Entities" value={summary.total_entities} accent="navy" />
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">District Risk Scores</h2>
          {districtLoading ? (
            <LoadingSkeleton variant="card" />
          ) : districtChartData.length > 0 ? (
            <ChartContainer
              title=""
              type="bar"
              data={districtChartData}
              xKey="district"
              series={[{ key: 'score', color: '#f59e0b', label: 'Risk Score' }]}
              height={300}
            />
          ) : (
            <EmptyState title="No district risk data" description="District risk scores will appear here." />
          )}
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Station Risk Scores</h2>
          {stationLoading ? (
            <LoadingSkeleton variant="card" />
          ) : stationChartData.length > 0 ? (
            <ChartContainer
              title=""
              type="bar"
              data={stationChartData}
              xKey="station"
              series={[{ key: 'score', color: '#ef4444', label: 'Risk Score' }]}
              height={300}
            />
          ) : (
            <EmptyState title="No station risk data" description="Station risk scores will appear here." />
          )}
        </Card>
      </div>

      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">District Risk Details</h2>
        {districtLoading ? (
          <LoadingSkeleton variant="table" rows={5} />
        ) : districtRisk && districtRisk.length > 0 ? (
          <DataTable
            columns={districtColumns}
            data={districtRisk}
            rowKey={(r) => r.district_id}
            emptyTitle="No district risk data"
            emptyDescription="District risk details will appear here."
            virtualized={false}
          />
        ) : (
          <EmptyState title="No district risk data" description="District risk details will appear here." />
        )}
      </Card>

      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Station Risk Details</h2>
        {stationLoading ? (
          <LoadingSkeleton variant="table" rows={5} />
        ) : stationRisk && stationRisk.length > 0 ? (
          <DataTable
            columns={stationColumns}
            data={stationRisk}
            rowKey={(r) => r.station_id}
            emptyTitle="No station risk data"
            emptyDescription="Station risk details will appear here."
            virtualized={false}
          />
        ) : (
          <EmptyState title="No station risk data" description="Station risk details will appear here." />
        )}
      </Card>

      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Predictions</h2>
        {predictionsLoading ? (
          <LoadingSkeleton variant="table" rows={5} />
        ) : predictions && predictions.length > 0 ? (
          <DataTable
            columns={predictionColumns}
            data={predictions}
            rowKey={(r) => r.entity_id}
            emptyTitle="No predictions"
            emptyDescription="Risk predictions will appear here."
            virtualized={false}
          />
        ) : (
          <EmptyState title="No predictions" description="Risk predictions will appear here." />
        )}
      </Card>

      {/* Details Modal */}
      <Modal
        isOpen={!!selectedEntity}
        onClose={() => setSelectedEntity(null)}
        title={selectedEntity ? `Risk Details — ${selectedEntity.entity_name}` : 'Risk Details'}
        footer={
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => setSelectedEntity(null)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        }
      >
        {selectedEntity && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm font-medium text-gray-700">Entity ID</span>
                <p className="text-sm text-gray-900">{selectedEntity.entity_id}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Entity Type</span>
                <p className="text-sm text-gray-900">{selectedEntity.entity_type}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Risk Score</span>
                <p className="text-sm text-gray-900">{selectedEntity.risk_score.toFixed(1)}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Risk Level</span>
                <Badge variant={RISK_LEVEL_VARIANT[selectedEntity.risk_level] ?? 'secondary'}>{selectedEntity.risk_level}</Badge>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Last Updated</span>
                <p className="text-sm text-gray-900">{selectedEntity.last_updated ? new Date(selectedEntity.last_updated).toLocaleString() : '-'}</p>
              </div>
            </div>

            <div>
              <span className="text-sm font-medium text-gray-700">Contributing Factors</span>
              <div className="mt-2 space-y-2">
                {selectedEntity.contributing_factors.map((factor, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-lg border border-gray-200 p-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{factor.name}</p>
                      <p className="text-xs text-gray-500">Contribution: {factor.contribution.toFixed(2)}</p>
                    </div>
                    <Badge variant="secondary">Weight: {factor.weight.toFixed(1)}</Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default RiskScoring;
