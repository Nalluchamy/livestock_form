import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getAnnotations,
  getAnnotationStats,
  submitGrade,
  adjudicateConsensus,
  flagQuality,
  uploadDatasetImage,
  AnnotationItem,
} from '../services/annotationService';
import {
  Upload,
  UserCheck,
  ShieldAlert,
  Camera,
  RefreshCw,
  Flag,
  Award,
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { useAuth } from '../context/AuthContext';

export const ExpertAnnotation: React.FC = () => {
  const queryClient = useQueryClient();
  const { user, hasRole } = useAuth();

  // Server-enforced role and identity from active session
  const graderId = user?.username || 'anonymous';
  const isSenior = user?.role === 'SENIOR_REVIEWER' || user?.role === 'ADMIN';
  const canGrade = hasRole('EXPERT_GRADER', 'SENIOR_REVIEWER', 'ADMIN');

  // Filters & selection
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [selectedSample, setSelectedSample] = useState<AnnotationItem | null>(null);

  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState<boolean>(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [customSampleId, setCustomSampleId] = useState<string>('');
  const [consentObtained, setConsentObtained] = useState<boolean>(true);

  // Quality flag modal
  const [showQualityModal, setShowQualityModal] = useState<boolean>(false);
  const [qualityReason, setQualityReason] = useState<string>('Obscured framing / glare on ribs.');

  // Annotation form state
  const [bcs, setBcs] = useState<number>(3.0);
  const [coatQuality, setCoatQuality] = useState<string>('Smooth');
  const [eyeCondition, setEyeCondition] = useState<string>('Clear');
  const [woundPresence, setWoundPresence] = useState<string>('None');
  const [mobility, setMobility] = useState<string>('Normal');
  const [appetite, setAppetite] = useState<string>('Good');
  const [weight, setWeight] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('B');
  const [notes, setNotes] = useState<string>('');

  // Senior Adjudication Form state
  const [consensusGrade, setConsensusGrade] = useState<string>('B');
  const [consensusRationale, setConsensusRationale] = useState<string>('');

  // Queries
  const { data: annotationData, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['annotations', statusFilter, graderId, isSenior],
    queryFn: () =>
      getAnnotations({
        status: statusFilter === 'ALL' ? undefined : statusFilter,
        viewer_id: graderId,
        is_senior: isSenior,
      }),
  });

  const { data: statsData } = useQuery({
    queryKey: ['annotation-stats'],
    queryFn: getAnnotationStats,
  });

  // Mutations
  const gradeMutation = useMutation({
    mutationFn: ({ sampleId, payload }: { sampleId: string; payload: any }) =>
      submitGrade(sampleId, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ['annotations'] });
      queryClient.invalidateQueries({ queryKey: ['annotation-stats'] });
      setSelectedSample(updated);
      alert(`Grade ${selectedGrade} successfully recorded under double-blind protocol.`);
    },
  });

  const consensusMutation = useMutation({
    mutationFn: ({ sampleId, payload }: { sampleId: string; payload: any }) =>
      adjudicateConsensus(sampleId, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ['annotations'] });
      queryClient.invalidateQueries({ queryKey: ['annotation-stats'] });
      setSelectedSample(updated);
      setConsensusRationale('');
      alert(`Consensus grade ${consensusGrade} adjudicated and finalized.`);
    },
  });

  const qualityMutation = useMutation({
    mutationFn: ({ sampleId, payload }: { sampleId: string; payload: any }) =>
      flagQuality(sampleId, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ['annotations'] });
      queryClient.invalidateQueries({ queryKey: ['annotation-stats'] });
      setSelectedSample(updated);
      setShowQualityModal(false);
      alert('Image marked as REJECTED due to quality or PII violation.');
    },
  });

  const uploadMutation = useMutation({
    mutationFn: uploadDatasetImage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['annotations'] });
      queryClient.invalidateQueries({ queryKey: ['annotation-stats'] });
      setShowUploadModal(false);
      setUploadFile(null);
      setCustomSampleId('');
      alert('Image uploaded, sanitized (EXIF scrubbed, 512x512 normalized) and queued for annotation.');
    },
  });

  const handleSelectSample = (sample: AnnotationItem) => {
    setSelectedSample(sample);
    if (sample.body_condition) setBcs(sample.body_condition);
    if (sample.coat_quality) setCoatQuality(sample.coat_quality);
    if (sample.eye_condition) setEyeCondition(sample.eye_condition);
    if (sample.wound_presence) setWoundPresence(sample.wound_presence);
    if (sample.mobility) setMobility(sample.mobility);
    if (sample.appetite) setAppetite(sample.appetite);
    if (sample.weight_if_available) setWeight(String(sample.weight_if_available));
  };

  const handleGradeSubmit = () => {
    if (!selectedSample) return;
    gradeMutation.mutate({
      sampleId: selectedSample.sample_id,
      payload: {
        grader_id: graderId,
        grade: selectedGrade,
        attributes: {
          body_condition: bcs,
          coat_quality: coatQuality,
          eye_condition: eyeCondition,
          wound_presence: woundPresence,
          mobility: mobility,
          appetite: appetite,
          weight_if_available: weight ? parseFloat(weight) : null,
        },
        notes: notes,
      },
    });
  };

  const handleConsensusSubmit = () => {
    if (!selectedSample || !consensusRationale.trim()) {
      alert('Please provide a clinical rationale for the consensus decision.');
      return;
    }
    consensusMutation.mutate({
      sampleId: selectedSample.sample_id,
      payload: {
        reviewer_id: graderId,
        final_grade: consensusGrade,
        rationale: consensusRationale,
      },
    });
  };

  const handleQualityFlagSubmit = () => {
    if (!selectedSample) return;
    qualityMutation.mutate({
      sampleId: selectedSample.sample_id,
      payload: {
        grader_id: graderId,
        reason: qualityReason,
      },
    });
  };

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    const formData = new FormData();
    formData.append('file', uploadFile);
    if (customSampleId) formData.append('sample_id', customSampleId);
    formData.append('species', 'cattle');
    formData.append('source_type', 'field_pilot');
    formData.append('contributor_id', graderId);
    formData.append('consent_obtained', String(consentObtained));
    uploadMutation.mutate(formData);
  };

  const isUrgent =
    selectedGrade === 'D' ||
    woundPresence === 'Severe' ||
    mobility === 'Unable to stand' ||
    bcs < 1.5 ||
    bcs > 4.5 ||
    eyeCondition === 'Severe infection';

  return (
    <div className="space-y-6">
      {/* Top Banner / Disclaimer */}
      <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg shadow-sm">
        <div className="flex items-start space-x-3">
          <ShieldAlert className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-amber-900">
            <span className="font-bold">MANDATORY CLINICAL DISCLAIMER:</span> Condition grade is an
            observational decision-support score, not a veterinary medical diagnosis. Urgent cases
            require immediate clinical examination by a licensed veterinarian.
          </div>
        </div>
      </div>

      {/* Header and Grader Role Switcher */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Award className="w-7 h-7 text-civic-teal" />
            Expert Livestock Annotation Workspace
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Standardized Cattle Condition Rubric v2.0 • Double-Blind Protocol Isolation • Strict
            Non-Inference Boundaries
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-lg flex items-center space-x-2 text-xs">
            <UserCheck className="w-4 h-4 text-civic-teal" />
            <div>
              <span className="text-slate-500 font-medium">Session: </span>
              <strong className="text-slate-900">{user?.username || 'Guest Viewer'}</strong>
              <span className="ml-2 px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-800">
                {user?.role || 'UNAUTHENTICATED'}
              </span>
            </div>
          </div>

          {canGrade && (
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-civic-teal text-white text-sm font-medium rounded-lg hover:bg-teal-700 transition"
            >
              <Upload className="w-4 h-4" />
              Ingest Image
            </button>
          )}
        </div>
      </div>

      {/* Live Pipeline Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-xs font-bold text-slate-400 uppercase">Tracked Samples</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {statsData?.total_samples ?? 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            {statsData?.pending_samples ?? 0} Pending • {statsData?.partially_annotated_samples ?? 0}{' '}
            Partial
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-xs font-bold text-slate-400 uppercase">Consensus Reached</div>
          <div className="text-2xl font-bold text-emerald-600 mt-1">
            {statsData?.consensus_reached_samples ?? 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">Ready for real training split</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-xs font-bold text-slate-400 uppercase">Inter-Expert Disagreements</div>
          <div className="text-2xl font-bold text-amber-600 mt-1">
            {statsData?.disagreement_samples ?? 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">Awaiting senior adjudication</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-xs font-bold text-slate-400 uppercase">Exact Agreement Rate</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {statsData?.exact_agreement_percentage ?? 0}%
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Across {statsData?.double_graded_samples ?? 0} double-graded pairs
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-slate-200 space-x-2 overflow-x-auto pb-1">
        {['ALL', 'PENDING', 'PARTIALLY_ANNOTATED', 'DISAGREEMENT', 'CONSENSUS_REACHED', 'REJECTED'].map(
          (tab) => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${
                statusFilter === tab
                  ? 'border-b-2 border-civic-teal text-civic-teal font-bold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              {tab.replace('_', ' ')}
            </button>
          )
        )}
      </div>

      {/* Main Dual-Panel Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Sample List / Queue (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-3 max-h-[700px] overflow-y-auto">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-400 uppercase">Task Queue</span>
            <button
              onClick={() => refetch()}
              className="text-xs text-civic-teal flex items-center gap-1 hover:underline"
            >
              <RefreshCw className="w-3 h-3" /> Refresh
            </button>
          </div>

          {isLoading ? (
            <LoadingSpinner />
          ) : isError ? (
            <ErrorState message={(error as any)?.message || 'Failed to load queue'} />
          ) : !annotationData?.items?.length ? (
            <div className="text-center py-8 text-slate-400 text-sm">
              No samples match the selected filter.
            </div>
          ) : (
            annotationData.items.map((sample) => {
              const isSelected = selectedSample?.sample_id === sample.sample_id;
              return (
                <div
                  key={sample.id}
                  onClick={() => handleSelectSample(sample)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-civic-teal bg-teal-50/50 shadow-sm'
                      : 'border-slate-100 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-900 text-sm">{sample.sample_id}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 font-bold rounded-full uppercase ${
                        sample.annotation_status === 'CONSENSUS_REACHED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : sample.annotation_status === 'DISAGREEMENT'
                          ? 'bg-amber-100 text-amber-800'
                          : sample.annotation_status === 'REJECTED'
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {sample.annotation_status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1 flex items-center justify-between">
                    <span>Species: {sample.species}</span>
                    <span>BCS: {sample.body_condition ?? 'Unset'}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Selected Sample Detail & Annotation Studio (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          {!selectedSample ? (
            <div className="text-center py-20 text-slate-400">
              <Camera className="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p className="font-medium">Select an image sample from the queue to start grading.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Sample Header & Quick Actions */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                <div>
                  <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                    {selectedSample.sample_id}
                    <span className="text-xs font-normal text-slate-500">
                      ({selectedSample.species})
                    </span>
                  </h2>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Storage: <code className="bg-slate-100 px-1 py-0.5 rounded">{selectedSample.image_path}</code>
                  </div>
                </div>

                <button
                  onClick={() => setShowQualityModal(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-rose-700 bg-rose-50 border border-rose-200 rounded-lg hover:bg-rose-100"
                >
                  <Flag className="w-3.5 h-3.5" /> Flag Quality / PII
                </button>
              </div>

              {/* Status and Double-Blind Isolation Bar */}
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs">
                <div>
                  <span className="font-semibold text-slate-600">Protocol Isolation: </span>
                  <span className="text-slate-900">
                    Grader 1: {selectedSample.expert_grader_1_id ? '✓ Submitted' : 'Pending'} •{' '}
                    Grader 2: {selectedSample.expert_grader_2_id ? '✓ Submitted' : 'Pending'}
                  </span>
                </div>
                {selectedSample.final_consensus_grade && (
                  <div className="font-bold text-emerald-700">
                    Final Consensus Grade: {selectedSample.final_consensus_grade}
                  </div>
                )}
              </div>

              {/* Urgent Escalation Warning Banner */}
              {isUrgent && (
                <div className="p-3 bg-rose-50 border-l-4 border-rose-600 rounded-r-lg text-xs text-rose-900 flex items-start gap-2">
                  <ShieldAlert className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">CLINICAL ESCALATION TRIGGERED:</span> Current parameters
                    indicate critical condition (Grade D / severe trauma / downer immobility). This
                    sample requires immediate veterinary triage upon completion.
                  </div>
                </div>
              )}

              {/* Image Preview & Attributes Form Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left: Sanitized Image Display */}
                <div>
                  <div className="border border-slate-200 rounded-xl overflow-hidden bg-slate-100 aspect-square flex items-center justify-center relative">
                    <img
                      src={`/${selectedSample.image_path}`}
                      alt={selectedSample.sample_id}
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        // Fallback placeholder if file not directly served
                        (e.target as HTMLElement).style.display = 'none';
                      }}
                    />
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400 p-4 text-center pointer-events-none">
                      <Camera className="w-10 h-10 mb-2 opacity-30" />
                      <span className="text-xs opacity-75">Sanitized Lateral Cattle Photo</span>
                      <span className="text-[10px] text-slate-400 mt-1">
                        512×512 Standardized RGB • EXIF Stripped
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right: Structured Clinical Entry Form */}
                <div className="space-y-4">
                  <div className="border-b pb-2">
                    <h3 className="text-xs font-bold text-slate-400 uppercase">
                      1. Photo-Observable Traits
                    </h3>
                  </div>

                  {/* BCS */}
                  <div>
                    <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                      <span>Body Condition Score (BCS 1.0 - 5.0)</span>
                      <span className="font-bold text-civic-teal">{bcs.toFixed(1)}</span>
                    </div>
                    <input
                      type="range"
                      min="1.0"
                      max="5.0"
                      step="0.1"
                      value={bcs}
                      onChange={(e) => setBcs(parseFloat(e.target.value))}
                      className="w-full accent-civic-teal"
                    />
                    <div className="flex justify-between text-[10px] text-slate-400">
                      <span>1.0 (Emaciated)</span>
                      <span>3.0 (Optimal)</span>
                      <span>5.0 (Obese)</span>
                    </div>
                  </div>

                  {/* Coat Quality */}
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      Coat / Hide Quality
                    </label>
                    <select
                      value={coatQuality}
                      onChange={(e) => setCoatQuality(e.target.value)}
                      className="w-full text-xs p-2 border rounded-lg bg-white"
                    >
                      <option value="Smooth">Smooth (Optimal sheen, no hair loss)</option>
                      <option value="Slightly rough">Slightly rough (Mild dullness)</option>
                      <option value="Rough">Rough (Noticeable patches, mange risk)</option>
                      <option value="Severe lesions">Severe lesions (Parasites, ulcerations)</option>
                    </select>
                  </div>

                  {/* Eye Condition */}
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      Eye Condition
                    </label>
                    <select
                      value={eyeCondition}
                      onChange={(e) => setEyeCondition(e.target.value)}
                      className="w-full text-xs p-2 border rounded-lg bg-white"
                    >
                      <option value="Clear">Clear (Bright, healthy cornea)</option>
                      <option value="Slight discharge">Slight discharge (Mild lacrimation)</option>
                      <option value="Cloudy">Cloudy (Corneal opacity)</option>
                      <option value="Severe infection">Severe infection (Pinkeye/perforation)</option>
                    </select>
                  </div>

                  {/* Wound Presence */}
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      External Wounds
                    </label>
                    <select
                      value={woundPresence}
                      onChange={(e) => setWoundPresence(e.target.value)}
                      className="w-full text-xs p-2 border rounded-lg bg-white"
                    >
                      <option value="None">None (Intact dermis)</option>
                      <option value="Minor">Minor (Superficial scratches)</option>
                      <option value="Moderate">Moderate (Localized open abrasions)</option>
                      <option value="Severe">Severe (Deep lacerations, necrosis)</option>
                    </select>
                  </div>

                  <div className="border-b pb-2 pt-2">
                    <h3 className="text-xs font-bold text-slate-400 uppercase flex items-center justify-between">
                      <span>2. Clinical Exam / Log Attributes</span>
                      <span className="text-[10px] text-amber-700 font-normal">
                        Never infer from photos
                      </span>
                    </h3>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-700 mb-1">Mobility</label>
                      <select
                        value={mobility}
                        onChange={(e) => setMobility(e.target.value)}
                        className="w-full text-xs p-2 border rounded-lg bg-white"
                      >
                        <option value="Normal">Normal gait</option>
                        <option value="Slight limp">Slight limp</option>
                        <option value="Lame">Lame</option>
                        <option value="Unable to stand">Unable to stand (Downer)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-700 mb-1">Appetite</label>
                      <select
                        value={appetite}
                        onChange={(e) => setAppetite(e.target.value)}
                        className="w-full text-xs p-2 border rounded-lg bg-white"
                      >
                        <option value="Good">Good intake</option>
                        <option value="Fair">Fair intake</option>
                        <option value="Poor">Poor intake</option>
                        <option value="None">None / Anorexic</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      Live Weight (kg, if measured)
                    </label>
                    <input
                      type="number"
                      placeholder="e.g. 520"
                      value={weight}
                      onChange={(e) => setWeight(e.target.value)}
                      className="w-full text-xs p-2 border rounded-lg bg-white"
                    />
                  </div>
                </div>
              </div>

              {/* Condition Grade Submission Section */}
              <div className="border-t pt-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900">
                    Assign Independent Expert Condition Grade
                  </h3>
                  <span className="text-xs text-slate-400">Acting as: {graderId}</span>
                </div>

                <div className="grid grid-cols-4 gap-3">
                  {[
                    { grade: 'A', label: 'Prime / Healthy', color: 'border-emerald-500 bg-emerald-50 text-emerald-800' },
                    { grade: 'B', label: 'Observation', color: 'border-blue-500 bg-blue-50 text-blue-800' },
                    { grade: 'C', label: 'Treatment', color: 'border-amber-500 bg-amber-50 text-amber-800' },
                    { grade: 'D', label: 'Critical / Urgent', color: 'border-rose-500 bg-rose-50 text-rose-800' },
                  ].map((tier) => (
                    <button
                      key={tier.grade}
                      type="button"
                      onClick={() => setSelectedGrade(tier.grade)}
                      className={`p-3 rounded-xl border text-center transition-all ${
                        selectedGrade === tier.grade
                          ? `${tier.color} ring-2 ring-offset-1 font-bold shadow-sm`
                          : 'border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="text-lg font-bold">Grade {tier.grade}</div>
                      <div className="text-[10px] mt-0.5">{tier.label}</div>
                    </button>
                  ))}
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">
                    Clinical Notes & Justification
                  </label>
                  <textarea
                    rows={2}
                    placeholder="Enter visual markers (e.g. rib prominence, clear lacrimal ducts) justifying assigned score..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="w-full text-xs p-2 border rounded-lg"
                  />
                </div>

                <button
                  onClick={handleGradeSubmit}
                  disabled={gradeMutation.isPending || selectedSample.annotation_status === 'CONSENSUS_REACHED'}
                  className="w-full py-2.5 bg-civic-teal text-white text-sm font-bold rounded-lg hover:bg-teal-700 transition disabled:opacity-50"
                >
                  {gradeMutation.isPending
                    ? 'Submitting Blind Grade...'
                    : selectedSample.annotation_status === 'CONSENSUS_REACHED'
                    ? 'Consensus Finalized (Grading Closed)'
                    : 'Submit Blind Expert Grade'}
                </button>
              </div>

              {/* Senior Adjudication Section (Visible to Senior Reviewer on Disagreement) */}
              {isSenior && selectedSample.annotation_status === 'DISAGREEMENT' && (
                <div className="border-t-2 border-amber-500 pt-4 mt-6 bg-amber-50/50 p-4 rounded-xl space-y-3">
                  <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
                    <UserCheck className="w-5 h-5 text-amber-600" />
                    Senior Expert Disagreement Adjudication
                  </div>
                  <p className="text-xs text-amber-800">
                    Grader 1 assigned <strong>{selectedSample.expert_grade_1}</strong> and Grader 2
                    assigned <strong>{selectedSample.expert_grade_2}</strong>. Review observations and
                    issue an authoritative consensus determination.
                  </p>

                  <div className="flex gap-3">
                    {['A', 'B', 'C', 'D'].map((g) => (
                      <button
                        key={g}
                        onClick={() => setConsensusGrade(g)}
                        className={`flex-1 py-2 text-xs font-bold rounded-lg border ${
                          consensusGrade === g
                            ? 'bg-amber-600 text-white border-amber-600'
                            : 'bg-white border-slate-200'
                        }`}
                      >
                        Grade {g}
                      </button>
                    ))}
                  </div>

                  <textarea
                    rows={2}
                    placeholder="Document clinical rationale for resolving inter-rater discrepancy..."
                    value={consensusRationale}
                    onChange={(e) => setConsensusRationale(e.target.value)}
                    className="w-full text-xs p-2 border rounded-lg bg-white"
                  />

                  <button
                    onClick={handleConsensusSubmit}
                    disabled={consensusMutation.isPending}
                    className="w-full py-2 bg-amber-600 text-white text-xs font-bold rounded-lg hover:bg-amber-700 transition"
                  >
                    Confirm Authoritative Consensus Decision
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Ingest Image Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Upload className="w-5 h-5 text-civic-teal" /> Ingest Livestock Image
            </h3>
            <p className="text-xs text-slate-500">
              Uploads are scrubbed of EXIF/GPS metadata, resized to 512×512, screened for PII, and
              logged into the provenance registry.
            </p>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Select Image File (JPEG, PNG, WebP)
                </label>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-teal-50 file:text-civic-teal hover:file:bg-teal-100"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Optional Sample ID / Animal ID
                </label>
                <input
                  type="text"
                  placeholder="e.g. COW-PILOT-042"
                  value={customSampleId}
                  onChange={(e) => setCustomSampleId(e.target.value)}
                  className="w-full text-xs p-2 border rounded-lg"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="consent"
                  checked={consentObtained}
                  onChange={(e) => setConsentObtained(e.target.checked)}
                  className="rounded text-civic-teal"
                />
                <label htmlFor="consent" className="text-xs text-slate-600">
                  Ranch/owner informed consent obtained for research collection.
                </label>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploadMutation.isPending || !uploadFile}
                  className="px-4 py-2 text-xs font-bold text-white bg-civic-teal hover:bg-teal-700 rounded-lg disabled:opacity-50"
                >
                  {uploadMutation.isPending ? 'Processing & Sanitizing...' : 'Upload & Sanitize'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Flag Quality Modal */}
      {showQualityModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-rose-700 flex items-center gap-2">
              <Flag className="w-5 h-5 text-rose-600" /> Flag Quality / PII Violation
            </h3>
            <p className="text-xs text-slate-500">
              Flagged samples will be quarantined from training datasets and marked as REJECTED.
            </p>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Reason for Quality Rejection
              </label>
              <textarea
                rows={3}
                value={qualityReason}
                onChange={(e) => setQualityReason(e.target.value)}
                className="w-full text-xs p-2 border rounded-lg"
                placeholder="Describe lighting defect, occlusion, extreme angle, or visible human face..."
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowQualityModal(false)}
                className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleQualityFlagSubmit}
                disabled={qualityMutation.isPending}
                className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-lg"
              >
                Confirm Rejection Flag
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
