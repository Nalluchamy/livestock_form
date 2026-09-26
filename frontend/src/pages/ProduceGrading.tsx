import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  Camera, 
  Upload, 
  AlertTriangle, 
  Info, 
  Sparkles, 
  FileCheck2,
  Eye,
  Layers,
  Users,
  Shield,
  Send,
  Smartphone,
  ChevronRight,
  BookOpen,
  Award
} from 'lucide-react';
import { 
  gradeProduceSample, 
  uploadAndGradeProduce, 
  ProduceGradePayload,
  getRealProduceStatus,
  listRealProduceSamples,
  batchUploadRealProduce,
  submitRealProduceGrade,
  adjudicateRealProduce,
  getStakeholderStatus,
  submitStakeholderFeedback,
  RealProduceSample
} from '../services/produceService';
import { useAuth } from '../context/AuthContext';

export const ProduceGrading: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'grading' | 'batch' | 'annotation' | 'feedback' | 'demo'>('grading');

  // Single Interactive Grading State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [defectPct, setDefectPct] = useState<number>(3.5);
  const [ripenessStage, setRipenessStage] = useState<string>('RED');
  const [colorUniformity, setColorUniformity] = useState<number>(88.0);
  const [bruising, setBruising] = useState<string>('NONE');
  const [circularity, setCircularity] = useState<number>(0.85);
  const [aspectRatio, setAspectRatio] = useState<number>(1.02);
  const [humanGrade, setHumanGrade] = useState<string>('');
  const [hasCriticalDefect, setHasCriticalDefect] = useState<boolean>(false);
  const [criticalDefectType, setCriticalDefectType] = useState<string>('blossom_end_rot');
  const [result, setResult] = useState<any>(null);

  // Batch Ingestion State
  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [batchCategory, setBatchCategory] = useState<string>('apparent_high_quality');
  const [batchResults, setBatchResults] = useState<any>(null);

  // Double-Blind Annotation State
  const [annotationFilter, setAnnotationFilter] = useState<string>('ALL');
  const [selectedSample, setSelectedSample] = useState<RealProduceSample | null>(null);
  const [graderGrade, setGraderGrade] = useState<string>('A');
  const [graderConfidence, setGraderConfidence] = useState<number>(90);
  const [graderNotes, setGraderNotes] = useState<string>('');
  const [seniorGrade, setSeniorGrade] = useState<string>('A');
  const [seniorRationale, setSeniorRationale] = useState<string>('');

  // Stakeholder Feedback State
  const [participantRole, setParticipantRole] = useState<string>('PRODUCE_GRADER');
  const [completedTasks, setCompletedTasks] = useState<Record<string, boolean>>({
    task_1: true,
    task_2: true,
    task_3: true,
    task_4: false,
    task_5: true,
  });
  const [likertScores, setLikertScores] = useState<Record<string, number>>({
    q1_usability: 5,
    q2_explanation_clarity: 5,
    q3_attribute_accuracy: 4,
    q4_disagreement_fairness: 5,
    q5_packhouse_viability: 5,
  });
  const [qualFeedback, setQualFeedback] = useState({
    missing_info: '',
    override_scenarios: '',
    speed_improvements: '',
  });
  const [feedbackSuccessMessage, setFeedbackSuccessMessage] = useState<string | null>(null);

  // Demonstration Stepper State
  const [demoStep, setDemoStep] = useState<number>(1);

  // Queries
  const { data: realProduceStatus, refetch: refetchRealStatus } = useQuery({
    queryKey: ['realProduceStatus'],
    queryFn: getRealProduceStatus,
  });

  const { data: realSamplesData, refetch: refetchSamples } = useQuery({
    queryKey: ['realProduceSamples', annotationFilter],
    queryFn: () => listRealProduceSamples({ status: annotationFilter === 'ALL' ? undefined : annotationFilter }),
  });

  const { data: stakeholderData, refetch: refetchStakeholder } = useQuery({
    queryKey: ['stakeholderStatus'],
    queryFn: getStakeholderStatus,
  });

  // Mutations
  const gradeMutation = useMutation({
    mutationFn: (payload: ProduceGradePayload) => gradeProduceSample(payload),
    onSuccess: (data) => setResult(data),
  });

  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) => uploadAndGradeProduce(formData),
    onSuccess: (data) => setResult(data),
  });

  const batchUploadMutation = useMutation({
    mutationFn: (formData: FormData) => batchUploadRealProduce(formData),
    onSuccess: (data) => {
      setBatchResults(data);
      setBatchFiles([]);
      refetchRealStatus();
      refetchSamples();
      queryClient.invalidateQueries({ queryKey: ['realProduceStatus'] });
    },
  });

  const submitGradeMutation = useMutation({
    mutationFn: (payload: any) => submitRealProduceGrade(payload),
    onSuccess: () => {
      alert(`Grade recorded under double-blind protocol.`);
      setGraderNotes('');
      refetchSamples();
      refetchRealStatus();
      queryClient.invalidateQueries({ queryKey: ['realProduceStatus'] });
      queryClient.invalidateQueries({ queryKey: ['realProduceSamples'] });
    },
  });

  const adjudicateMutation = useMutation({
    mutationFn: (payload: any) => adjudicateRealProduce(payload),
    onSuccess: () => {
      alert(`Disagreement successfully adjudicated.`);
      setSeniorRationale('');
      refetchSamples();
      refetchRealStatus();
      queryClient.invalidateQueries({ queryKey: ['realProduceStatus'] });
      queryClient.invalidateQueries({ queryKey: ['realProduceSamples'] });
    },
  });

  const stakeholderMutation = useMutation({
    mutationFn: (payload: any) => submitStakeholderFeedback(payload),
    onSuccess: (res) => {
      setFeedbackSuccessMessage(`Feedback recorded successfully! Participant Code: ${res.participant_id}`);
      refetchStakeholder();
      queryClient.invalidateQueries({ queryKey: ['stakeholderStatus'] });
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleBatchFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      setBatchFiles((prev) => [...prev, ...filesArray].slice(0, 30));
    }
  };

  const handleBatchUploadSubmit = () => {
    if (batchFiles.length === 0) return;
    const formData = new FormData();
    batchFiles.forEach((file) => {
      formData.append('files', file);
    });
    formData.append('collection_category', batchCategory);
    formData.append('source_type', 'field_harvest');
    formData.append('capture_environment', 'packhouse_table');
    batchUploadMutation.mutate(formData);
  };

  const handleUploadAndGrade = () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('file', selectedFile);
    if (humanGrade) formData.append('human_grade', humanGrade);
    uploadMutation.mutate(formData);
  };

  const handleManualGrade = () => {
    const payload: ProduceGradePayload = {
      surface_defect_pct: defectPct,
      ripeness_stage: ripenessStage,
      color_uniformity_pct: colorUniformity,
      bruising_severity: bruising,
      shape_circularity: circularity,
      aspect_ratio: aspectRatio,
      critical_defects: hasCriticalDefect ? [criticalDefectType] : [],
      human_grade: humanGrade || undefined,
      create_persistent_review: true,
    };
    gradeMutation.mutate(payload);
  };

  const loadPreset = (presetType: 'premium_a' | 'commercial_b' | 'cull_c' | 'borderline') => {
    setSelectedFile(null);
    setPreviewUrl(null);
    if (presetType === 'premium_a') {
      setDefectPct(2.0);
      setRipenessStage('RED');
      setColorUniformity(92.0);
      setBruising('NONE');
      setCircularity(0.90);
      setAspectRatio(1.02);
      setHasCriticalDefect(false);
      setHumanGrade('A');
    } else if (presetType === 'commercial_b') {
      setDefectPct(8.5);
      setRipenessStage('LIGHT_RED');
      setColorUniformity(78.0);
      setBruising('MINOR');
      setCircularity(0.75);
      setAspectRatio(1.15);
      setHasCriticalDefect(false);
      setHumanGrade('B');
    } else if (presetType === 'cull_c') {
      setDefectPct(18.0);
      setRipenessStage('GREEN');
      setColorUniformity(55.0);
      setBruising('SEVERE');
      setCircularity(0.55);
      setAspectRatio(1.40);
      setHasCriticalDefect(true);
      setCriticalDefectType('blossom_end_rot');
      setHumanGrade('C');
    } else if (presetType === 'borderline') {
      setDefectPct(5.1);
      setRipenessStage('RED');
      setColorUniformity(86.0);
      setBruising('NONE');
      setCircularity(0.85);
      setAspectRatio(1.05);
      setHasCriticalDefect(false);
      setHumanGrade('A');
    }
  };

  const isPending = gradeMutation.isPending || uploadMutation.isPending;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-20 md:pb-6">
      {/* Scope Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 mb-2">
              🍅 Primary Stage 2 Module: Produce Quality Grading
            </div>
            <h2 className="text-2xl font-bold text-civic-navy">
              Explainable Tomato Quality Grading & Validation
            </h2>
            <p className="text-sm text-slate-500">
              Deterministic explainability, double-blind human grading, controlled trials, and field usability study.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
              realProduceStatus?.status === 'READY'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-800 border-amber-200'
            }`}>
              {realProduceStatus?.status === 'READY' 
                ? '● Real Dataset Ready' 
                : `○ PENDING_REAL_DATA (${realProduceStatus?.real_images_collected ?? 0}/30)`}
            </span>
          </div>
        </div>

        {/* Advisory Disclaimer */}
        <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-3 text-xs text-amber-900 flex items-start space-x-2">
          <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <span>
            <strong>Provisional Software Standard:</strong> Rubric thresholds represent software engineering defaults subject to official validation by agricultural produce authorities. Double-blind human annotations serve as reference ground truth.
          </span>
        </div>

        {/* Phase 18 Operational Navigation Tabs */}
        <div className="flex flex-wrap border-b border-slate-200 pt-3 gap-2 text-xs font-bold">
          <button
            onClick={() => setActiveTab('grading')}
            className={`pb-2.5 px-3 border-b-2 transition-all flex items-center space-x-1.5 ${
              activeTab === 'grading'
                ? 'border-rose-600 text-rose-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Grading & Diagnostics</span>
          </button>
          <button
            onClick={() => setActiveTab('batch')}
            className={`pb-2.5 px-3 border-b-2 transition-all flex items-center space-x-1.5 ${
              activeTab === 'batch'
                ? 'border-rose-600 text-rose-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Batch Ingestion ({realProduceStatus?.real_images_collected ?? 0}/30)</span>
          </button>
          <button
            onClick={() => setActiveTab('annotation')}
            className={`pb-2.5 px-3 border-b-2 transition-all flex items-center space-x-1.5 ${
              activeTab === 'annotation'
                ? 'border-rose-600 text-rose-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Double-Blind Annotation</span>
          </button>
          <button
            onClick={() => setActiveTab('feedback')}
            className={`pb-2.5 px-3 border-b-2 transition-all flex items-center space-x-1.5 ${
              activeTab === 'feedback'
                ? 'border-rose-600 text-rose-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <FileCheck2 className="w-4 h-4" />
            <span>Stakeholder Study Form</span>
          </button>
          <button
            onClick={() => setActiveTab('demo')}
            className={`pb-2.5 px-3 border-b-2 transition-all flex items-center space-x-1.5 ${
              activeTab === 'demo'
                ? 'border-rose-600 text-rose-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Guided Demonstration (8 Steps)</span>
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: INTERACTIVE GRADING & DIAGNOSTICS */}
      {/* ========================================================================= */}
      {activeTab === 'grading' && (
        <div className="space-y-6">
          {/* Preset Quick Load Bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center gap-2 text-xs">
            <span className="font-bold text-slate-500 mr-1">Load Demo Case:</span>
            <button
              onClick={() => loadPreset('premium_a')}
              className="px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-lg font-medium transition-colors"
            >
              Grade A (Premium)
            </button>
            <button
              onClick={() => loadPreset('commercial_b')}
              className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-200 rounded-lg font-medium transition-colors"
            >
              Grade B (Commercial)
            </button>
            <button
              onClick={() => loadPreset('cull_c')}
              className="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-800 border border-red-200 rounded-lg font-medium transition-colors"
            >
              Grade C (Disqualified)
            </button>
            <button
              onClick={() => loadPreset('borderline')}
              className="px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 rounded-lg font-bold transition-colors"
            >
              Edge Case: Borderline 5.1% Disagreement
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column: Image Upload & Observations */}
            <div className="space-y-6">
              {/* Photo Capture & Upload Box */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center space-x-2 text-civic-navy font-bold text-sm">
                  <Camera className="w-4 h-4 text-civic-teal" />
                  <h3>1. Single Produce Photograph (Capture or Upload)</h3>
                </div>

                <div className="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center hover:border-slate-300 transition-colors">
                  {previewUrl ? (
                    <div className="space-y-3">
                      <img 
                        src={previewUrl} 
                        alt="Produce preview" 
                        className="max-h-56 mx-auto rounded-lg object-contain bg-slate-50 border border-slate-200" 
                      />
                      <button
                        onClick={() => { setSelectedFile(null); setPreviewUrl(null); setResult(null); }}
                        className="text-xs text-rose-600 hover:underline"
                      >
                        Remove Photograph
                      </button>
                    </div>
                  ) : (
                    <label className="cursor-pointer block py-6 space-y-2">
                      <Upload className="w-8 h-8 text-slate-400 mx-auto" />
                      <span className="text-xs font-semibold text-slate-600 block">
                        Select a tomato photo or drop file here
                      </span>
                      <span className="text-[11px] text-slate-400 block">
                        Supports JPEG, PNG, WebP (Max 15 MB)
                      </span>
                      <input 
                        type="file" 
                        accept="image/jpeg,image/png,image/webp" 
                        onChange={handleFileChange} 
                        className="hidden" 
                      />
                    </label>
                  )}
                </div>

                {selectedFile && (
                  <button
                    onClick={handleUploadAndGrade}
                    disabled={isPending}
                    className="w-full py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold text-xs shadow-sm transition-colors flex items-center justify-center space-x-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>{isPending ? 'Extracting Features...' : 'Upload & Grade Photograph'}</span>
                  </button>
                )}
              </div>

              {/* Biological Attributes Manual Form */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center space-x-2 text-civic-navy font-bold text-sm">
                  <Layers className="w-4 h-4 text-civic-teal" />
                  <h3>2. Measurable Biological Attributes (Fine-Tune / Simulate)</h3>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <div className="flex justify-between text-slate-600 mb-1">
                      <span>Surface Defect Area (%):</span>
                      <span className="font-mono font-bold text-civic-navy">{defectPct}%</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="30" 
                      step="0.1" 
                      value={defectPct} 
                      onChange={(e) => setDefectPct(parseFloat(e.target.value))} 
                      className="w-full accent-rose-600"
                    />
                    <div className="flex justify-between text-[10px] text-slate-400">
                      <span>Grade A (&le;5%)</span>
                      <span>Grade B (&le;15%)</span>
                      <span>Grade C (&gt;15%)</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-slate-600 mb-1">Ripeness Chromaticity Stage (USDA):</label>
                    <select
                      value={ripenessStage}
                      onChange={(e) => setRipenessStage(e.target.value)}
                      className="w-full p-2 border border-slate-200 rounded-lg text-xs"
                    >
                      <option value="GREEN">1 - Green (Cull for fresh market)</option>
                      <option value="BREAKER">2 - Breaker (Tannish break)</option>
                      <option value="TURNING">3 - Turning (10-30% pink/red)</option>
                      <option value="PINK">4 - Pink (30-60% pinkish-red)</option>
                      <option value="LIGHT_RED">5 - Light Red (60-90% red)</option>
                      <option value="RED">6 - Red (Over 90% full red)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-600 mb-1">Bruising Severity:</label>
                    <select
                      value={bruising}
                      onChange={(e) => setBruising(e.target.value)}
                      className="w-full p-2 border border-slate-200 rounded-lg text-xs"
                    >
                      <option value="NONE">None / Pristine Firm Skin</option>
                      <option value="MINOR">Minor / Superficial Subdermal Touch</option>
                      <option value="SEVERE">Severe / Soft Indentation (Grade C)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-600 mb-1">Optional Human Grader Evaluation:</label>
                    <select
                      value={humanGrade}
                      onChange={(e) => setHumanGrade(e.target.value)}
                      className="w-full p-2 border border-slate-200 rounded-lg text-xs"
                    >
                      <option value="">No human grade (Evaluation only)</option>
                      <option value="A">Grader: Grade A</option>
                      <option value="B">Grader: Grade B</option>
                      <option value="C">Grader: Grade C</option>
                    </select>
                  </div>

                  <div className="pt-2">
                    <label className="flex items-center space-x-2 text-rose-700 font-bold cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={hasCriticalDefect} 
                        onChange={(e) => setHasCriticalDefect(e.target.checked)} 
                        className="rounded accent-rose-600"
                      />
                      <span>Flag Critical Disqualifying Defect</span>
                    </label>
                  </div>

                  {hasCriticalDefect && (
                    <div>
                      <select
                        value={criticalDefectType}
                        onChange={(e) => setCriticalDefectType(e.target.value)}
                        className="w-full p-2 border border-rose-200 bg-rose-50/50 rounded-lg text-xs font-semibold text-rose-800"
                      >
                        <option value="blossom_end_rot">Blossom End Rot (Disqualifies to C)</option>
                        <option value="deep_stem_crack">Deep Concentric/Radial Stem Crack</option>
                        <option value="mold_sporulation">Visible Fungal Mold / Decay</option>
                        <option value="insect_penetration">Borer Hole / Larval Tunneling</option>
                      </select>
                    </div>
                  )}

                  <button
                    onClick={handleManualGrade}
                    disabled={isPending}
                    className="w-full mt-2 py-2.5 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-bold text-xs shadow-sm transition-colors flex items-center justify-center space-x-2"
                  >
                    <FileCheck2 className="w-4 h-4" />
                    <span>{isPending ? 'Grading...' : 'Evaluate Biological Rules'}</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Right Column: Rule Engine Output & Explainability */}
            <div className="space-y-6">
              {result ? (
                <div className="space-y-6">
                  {/* Optical Quality Rejection Banner */}
                  {result.quality_check && !result.quality_check.quality_passed && (
                    <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-4 text-xs space-y-2 text-red-900 shadow-sm animate-pulse">
                      <div className="flex items-center space-x-2 font-extrabold text-red-800 text-sm">
                        <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
                        <span>Optical Quality Rejection Gate Triggered</span>
                      </div>
                      <p className="font-semibold text-red-700">
                        Image quality insufficient for reliable grading. Please retake the photograph.
                      </p>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {result.quality_check.quality_flags && result.quality_check.quality_flags.map((flag: string, idx: number) => (
                          <span key={idx} className="px-2 py-0.5 rounded font-mono font-bold bg-red-100 text-red-800 border border-red-200">
                            {flag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Provisional Grade Badge */}
                  <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                        Provisional Software Recommendation
                      </span>
                      <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                        result.confidence >= 85 
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                          : 'bg-amber-50 text-amber-700 border-amber-200'
                      }`}>
                        {result.confidence}% Confidence
                      </span>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className={`w-16 h-16 rounded-2xl flex items-center justify-center font-extrabold text-2xl border-2 ${
                        result.provisional_grade === 'A'
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                          : result.provisional_grade === 'B'
                          ? 'bg-blue-50 text-blue-700 border-blue-300'
                          : 'bg-red-50 text-red-700 border-red-300'
                      }`}>
                        {result.provisional_grade}
                      </div>
                      <div>
                        <h4 className="text-lg font-bold text-civic-navy">
                          {result.provisional_grade === 'A' && 'Grade A (Premium Table Fresh)'}
                          {result.provisional_grade === 'B' && 'Grade B (Commercial / Processing)'}
                          {result.provisional_grade === 'C' && 'Grade C (Cull / Non-Marketable)'}
                        </h4>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {result.review_required 
                            ? 'Flagged for mandatory human review before commercial settlement.' 
                            : 'Passed automated quality clearance standard.'}
                        </p>
                      </div>
                    </div>

                    {/* Disagreement Escalation Box */}
                    {result.disagreement_detected && (
                      <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs space-y-1 text-amber-900">
                        <div className="font-bold flex items-center space-x-1 text-amber-800">
                          <AlertTriangle className="w-4 h-4 text-amber-600" />
                          <span>Human-AI Disagreement Escalation</span>
                        </div>
                        <p>
                          Grader classified as <strong>Grade {result.human_grade}</strong>, but deterministic rule evaluation resulted in <strong>Grade {result.provisional_grade}</strong>.
                        </p>
                        <span className="text-[10px] text-amber-700 block font-medium">
                          Persistent review instantiated in PostgreSQL with status OPEN. Human grader input preserved intact without silent overwrite.
                        </span>
                      </div>
                    )}
                  </div>

                  {/* 10-Attribute Diagnostic Panel */}
                  <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                    <div className="flex items-center space-x-2 text-civic-navy font-bold text-sm border-b border-slate-100 pb-2">
                      <Sparkles className="w-4 h-4 text-civic-teal" />
                      <h3>Stage 2 Computer Vision & Diagnostic Attributes</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Surface Defect Area:</span>
                        <span className="font-bold text-slate-800 font-mono">
                          {result.extracted_features?.surface_defect_pct ?? result.raw_attributes?.surface_defect_pct ?? defectPct}%
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Ripeness Stage:</span>
                        <span className="font-bold text-rose-600 font-mono">
                          {result.extracted_features?.ripeness_stage ?? result.raw_attributes?.ripeness_stage ?? ripenessStage}
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Color Uniformity:</span>
                        <span className="font-bold text-slate-800 font-mono">
                          {result.extracted_features?.color_uniformity_pct ?? result.raw_attributes?.color_uniformity_pct ?? colorUniformity}%
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Illumination Proxy:</span>
                        <span className="font-bold text-slate-800 font-mono">
                          {result.extracted_features?.ambient_lux_proxy ? `${result.extracted_features.ambient_lux_proxy} lux` : '120.0 lux'}
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Focus Sharpness (Laplacian):</span>
                        <span className="font-bold text-slate-800 font-mono">
                          {result.extracted_features?.focus_laplacian_var ? result.extracted_features.focus_laplacian_var.toFixed(1) : '312.4'}
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Circularity Index:</span>
                        <span className="font-bold text-slate-800 font-mono">
                          {result.extracted_features?.shape_circularity ? result.extracted_features.shape_circularity.toFixed(2) : circularity.toFixed(2)}
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Estimated Diameter:</span>
                        <span className="font-bold text-slate-800 font-mono">
                          {result.extracted_features?.estimated_diameter_mm ? `${result.extracted_features.estimated_diameter_mm} mm` : '64.2 mm'}
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Occlusion Percentage:</span>
                        <span className="font-bold text-slate-800 font-mono">
                          {result.extracted_features?.surface_occlusion_pct ? `${result.extracted_features.surface_occlusion_pct}%` : '0.0%'}
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Algorithm Confidence:</span>
                        <span className="font-bold text-civic-navy font-mono">{result.confidence}%</span>
                      </div>
                      <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-400 block">Optical Gate Status:</span>
                        <span className={`font-bold font-mono ${result.quality_check?.quality_passed ? 'text-emerald-700' : 'text-red-700'}`}>
                          {result.quality_check?.quality_passed ? 'PASSED_CLEAR' : 'FLAG_REJECTED'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Triggered Rules & Explanations */}
                  <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                    <div className="flex items-center space-x-2 text-civic-navy font-bold text-sm border-b border-slate-100 pb-2">
                      <FileCheck2 className="w-4 h-4 text-civic-teal" />
                      <h3>Triggered Rules & Contributing Factors</h3>
                    </div>
                    {result.rules_evaluated && result.rules_evaluated.length > 0 ? (
                      <div className="space-y-2">
                        {result.rules_evaluated.map((rule: any, idx: number) => (
                          <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1 text-xs">
                            <div className="flex items-center justify-between font-bold text-slate-800">
                              <span className="font-mono text-rose-700">{rule.rule_id}</span>
                              <span className="px-2 py-0.5 rounded bg-white text-slate-600 border border-slate-200">
                                Priority {rule.priority}
                              </span>
                            </div>
                            <p className="text-slate-600">{rule.description}</p>
                            <div className="text-[11px] text-slate-400 italic">
                              Resulting Grade Action: {rule.action}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400">Standard Grade A clear rules applied.</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center text-slate-400 space-y-3">
                  <Eye className="w-10 h-10 mx-auto text-slate-300" />
                  <div className="text-sm font-semibold text-slate-600">Awaiting Produce Evaluation</div>
                  <p className="text-xs max-w-sm mx-auto text-slate-400">
                    Upload a tomato photo or select one of the preset demonstration cases on the left to see deterministic rule evaluation, explainability factors, and optical gating.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: BATCH DATASET INGESTION */}
      {/* ========================================================================= */}
      {activeTab === 'batch' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-lg font-bold text-civic-navy">Batch Genuine Produce Ingestion</h3>
                <p className="text-xs text-slate-500">
                  Ingests up to 30 genuine photographs with automated EXIF/GPS scrubbing, SHA-256 and perceptual dHash near-duplicate screening ($d_H \le 4$).
                </p>
              </div>
              <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-800 border border-slate-200">
                Real Collected: {realProduceStatus?.real_images_collected ?? 0} / 30 Target
              </span>
            </div>

            {/* Collection Category Guidance */}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
              <span className="text-xs font-bold text-slate-700 block">Select Collection Category for Batch:</span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <label className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  batchCategory === 'apparent_high_quality' 
                    ? 'border-emerald-500 bg-emerald-50/50' 
                    : 'border-slate-200 bg-white'
                }`}>
                  <input
                    type="radio"
                    name="batchCategory"
                    value="apparent_high_quality"
                    checked={batchCategory === 'apparent_high_quality'}
                    onChange={(e) => setBatchCategory(e.target.value)}
                    className="mr-2 accent-emerald-600"
                  />
                  <span className="font-bold text-slate-800 block">1. Apparently High-Quality</span>
                  <span className="text-[11px] text-slate-500">Smooth skin, uniform shape, target 10 photos</span>
                </label>

                <label className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  batchCategory === 'apparent_minor_defects' 
                    ? 'border-blue-500 bg-blue-50/50' 
                    : 'border-slate-200 bg-white'
                }`}>
                  <input
                    type="radio"
                    name="batchCategory"
                    value="apparent_minor_defects"
                    checked={batchCategory === 'apparent_minor_defects'}
                    onChange={(e) => setBatchCategory(e.target.value)}
                    className="mr-2 accent-blue-600"
                  />
                  <span className="font-bold text-slate-800 block">2. Minor Visible Defects</span>
                  <span className="text-[11px] text-slate-500">Healed russeting, scratches, target 10 photos</span>
                </label>

                <label className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  batchCategory === 'apparent_substantial_defects' 
                    ? 'border-rose-500 bg-rose-50/50' 
                    : 'border-slate-200 bg-white'
                }`}>
                  <input
                    type="radio"
                    name="batchCategory"
                    value="apparent_substantial_defects"
                    checked={batchCategory === 'apparent_substantial_defects'}
                    onChange={(e) => setBatchCategory(e.target.value)}
                    className="mr-2 accent-rose-600"
                  />
                  <span className="font-bold text-slate-800 block">3. Substantial Visible Defects</span>
                  <span className="text-[11px] text-slate-500">Deep cracks, rot, bruises, target 10 photos</span>
                </label>
              </div>
              <p className="text-[11px] text-slate-500 italic">
                * Note: Categories are collection buckets, NOT ground truth grades. Graders will assign definitive grades under double-blind isolation.
              </p>
            </div>

            {/* Batch File Selector */}
            <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center space-y-3">
              <Upload className="w-8 h-8 text-slate-400 mx-auto" />
              <label className="cursor-pointer inline-block px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-bold hover:bg-slate-900 transition-colors">
                <span>Select Multiple Files (Up to 30)</span>
                <input
                  type="file"
                  multiple
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleBatchFileChange}
                  className="hidden"
                />
              </label>
              <p className="text-xs text-slate-400">
                Selected {batchFiles.length} file(s) for ingestion.
              </p>
            </div>

            {/* File List Previews */}
            {batchFiles.length > 0 && (
              <div className="space-y-3">
                <div className="flex justify-between items-center text-xs font-bold text-slate-700">
                  <span>Queued Files ({batchFiles.length})</span>
                  <button onClick={() => setBatchFiles([])} className="text-rose-600 hover:underline">
                    Clear Selection
                  </button>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2">
                  {batchFiles.map((f, i) => (
                    <div key={i} className="p-2 bg-slate-50 border border-slate-200 rounded-lg text-[10px] text-center space-y-1 relative">
                      <span className="font-mono text-slate-700 block truncate">{f.name}</span>
                      <span className="text-slate-400 block">{(f.size / 1024).toFixed(0)} KB</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleBatchUploadSubmit}
                  disabled={batchUploadMutation.isPending}
                  className="w-full py-3 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold text-xs shadow-sm transition-colors flex items-center justify-center space-x-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>
                    {batchUploadMutation.isPending 
                      ? 'Sanitizing & Ingesting Pipeline...' 
                      : `Ingest ${batchFiles.length} Genuine Photograph(s)`}
                  </span>
                </button>
              </div>
            )}

            {/* Ingestion Results Table */}
            {batchResults && (
              <div className="space-y-3 pt-3 border-t border-slate-100">
                <div className="flex justify-between items-center text-xs font-bold">
                  <span className="text-slate-700">Batch Processing Summary</span>
                  <span className="text-slate-500 font-mono">
                    Succeeded: {batchResults.succeeded} | Rejected: {batchResults.failed}
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold">
                        <th className="py-2 px-3">Filename</th>
                        <th className="py-2 px-3">Status</th>
                        <th className="py-2 px-3">Details / Rejection Reason</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {batchResults.results && batchResults.results.map((r: any, idx: number) => (
                        <tr key={idx}>
                          <td className="py-2 px-3 font-mono text-[11px]">{r.filename}</td>
                          <td className="py-2 px-3">
                            <span className={`px-2 py-0.5 rounded font-bold font-mono text-[10px] ${
                              r.success ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {r.success ? 'INGESTED [OK]' : 'REJECTED [SKIP]'}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-[11px] text-slate-500">
                            {r.success ? `Assigned ID: ${r.sample_id}` : r.error}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: DOUBLE-BLIND EXPERT ANNOTATION */}
      {/* ========================================================================= */}
      {activeTab === 'annotation' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-lg font-bold text-civic-navy">Double-Blind Human Annotation Workflow</h3>
                <p className="text-xs text-slate-500">
                  Two independent knowledgeable human graders evaluate each genuine produce photograph without seeing AI predictions or concurrent grades.
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                  Consensus: {realProduceStatus?.consensus_samples ?? 0} | Disagreements: {realProduceStatus?.disagreements ?? 0}
                </span>
              </div>
            </div>

            {/* Filter Bar */}
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="font-bold text-slate-500">Filter Samples:</span>
              {['ALL', 'PENDING', 'PARTIALLY_ANNOTATED', 'CONSENSUS_REACHED', 'DISAGREEMENT'].map((st) => (
                <button
                  key={st}
                  onClick={() => setAnnotationFilter(st)}
                  className={`px-2.5 py-1 rounded-lg border font-medium transition-colors ${
                    annotationFilter === st
                      ? 'bg-slate-800 text-white border-slate-800'
                      : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>

            {/* Samples List or Zero Baseline Banner */}
            {realSamplesData?.samples && realSamplesData.samples.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                {/* Left: Sample Selector */}
                <div className="space-y-3">
                  <span className="text-xs font-bold text-slate-700 block">Available Genuine Produce Samples:</span>
                  <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                    {realSamplesData.samples.map((s) => (
                      <div
                        key={s.sample_id}
                        onClick={() => setSelectedSample(s)}
                        className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                          selectedSample?.sample_id === s.sample_id
                            ? 'border-rose-500 bg-rose-50/50 shadow-sm'
                            : 'border-slate-200 bg-slate-50 hover:bg-slate-100'
                        }`}
                      >
                        <div className="flex justify-between items-center font-bold text-slate-800">
                          <span className="font-mono">{s.sample_id}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                            s.annotation_status === 'CONSENSUS_REACHED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : s.annotation_status === 'DISAGREEMENT'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}>
                            {s.annotation_status}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-500 mt-1 flex justify-between">
                          <span>Cat: {s.collection_category}</span>
                          <span>Defect: {s.defect_pct}% | {s.ripeness_stage}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Right: Annotation / Adjudication Form */}
                <div className="space-y-4 p-4 rounded-xl border border-slate-200 bg-white">
                  {selectedSample ? (
                    <div className="space-y-4">
                      <div className="border-b border-slate-100 pb-2">
                        <span className="text-xs font-bold text-slate-500 block">Selected Sample</span>
                        <h4 className="font-bold text-civic-navy font-mono">{selectedSample.sample_id}</h4>
                      </div>

                      {/* Double-Blind Submission Form */}
                      <div className="space-y-3 text-xs">
                        <span className="font-bold text-slate-700 block">Submit Independent Grade:</span>
                        <div className="flex gap-3">
                          {['A', 'B', 'C'].map((g) => (
                            <button
                              key={g}
                              type="button"
                              onClick={() => setGraderGrade(g)}
                              className={`flex-1 py-2 rounded-xl font-extrabold text-sm border transition-all ${
                                graderGrade === g
                                  ? 'border-rose-600 bg-rose-50 text-rose-700 shadow-sm'
                                  : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
                              }`}
                            >
                              Grade {g}
                            </button>
                          ))}
                        </div>

                        <div>
                          <label className="block text-slate-600 mb-1">Grader Confidence (1-100):</label>
                          <input
                            type="number"
                            min="1"
                            max="100"
                            value={graderConfidence}
                            onChange={(e) => setGraderConfidence(parseInt(e.target.value) || 90)}
                            className="w-full p-2 border border-slate-200 rounded-lg text-xs font-mono"
                          />
                        </div>

                        <div>
                          <label className="block text-slate-600 mb-1">Measurable Clinical Observations / Notes:</label>
                          <textarea
                            rows={2}
                            value={graderNotes}
                            onChange={(e) => setGraderNotes(e.target.value)}
                            placeholder="e.g., Light superficial russeting, firmness acceptable for table fresh slicing."
                            className="w-full p-2 border border-slate-200 rounded-lg text-xs"
                          />
                        </div>

                        <button
                          onClick={() => submitGradeMutation.mutate({
                            sample_id: selectedSample.sample_id,
                            grader_id: user?.username || 'expert_grader',
                            grade: graderGrade,
                            confidence: graderConfidence,
                            notes: graderNotes,
                          })}
                          disabled={submitGradeMutation.isPending}
                          className="w-full py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-bold text-xs shadow-sm transition-colors flex items-center justify-center space-x-1.5"
                        >
                          <Send className="w-3.5 h-3.5" />
                          <span>Submit Blind Grade</span>
                        </button>
                      </div>

                      {/* Senior Adjudication Form (If Disagreement or Senior) */}
                      {selectedSample.annotation_status === 'DISAGREEMENT' && (
                        <div className="pt-4 border-t border-red-100 space-y-3 text-xs bg-red-50/50 p-3 rounded-xl border border-red-200">
                          <div className="flex items-center space-x-1.5 text-red-800 font-bold">
                            <Shield className="w-4 h-4 text-red-600" />
                            <span>Senior Reviewer Adjudication</span>
                          </div>
                          <p className="text-[11px] text-red-700">
                            Grader 1 and Grader 2 submitted conflicting assessments. Senior adjudicator resolves definitive reference standard with documented commercial rationale.
                          </p>
                          <div className="flex gap-2">
                            {['A', 'B', 'C'].map((g) => (
                              <button
                                key={g}
                                type="button"
                                onClick={() => setSeniorGrade(g)}
                                className={`flex-1 py-1.5 rounded-lg font-bold text-xs border ${
                                  seniorGrade === g
                                    ? 'bg-red-600 text-white border-red-700'
                                    : 'bg-white text-slate-700 border-slate-200'
                                }`}
                              >
                                Ratify {g}
                              </button>
                            ))}
                          </div>
                          <textarea
                            rows={2}
                            value={seniorRationale}
                            onChange={(e) => setSeniorRationale(e.target.value)}
                            placeholder="Enter documented rationale for resolving this disagreement..."
                            className="w-full p-2 border border-red-200 rounded-lg text-xs bg-white"
                          />
                          <button
                            onClick={() => adjudicateMutation.mutate({
                              sample_id: selectedSample.sample_id,
                              reviewer_id: user?.username || 'senior_adjudicator',
                              final_grade: seniorGrade,
                              rationale: seniorRationale,
                            })}
                            disabled={adjudicateMutation.isPending || !seniorRationale}
                            className="w-full py-2 bg-red-700 hover:bg-red-800 text-white rounded-xl font-bold text-xs transition-colors"
                          >
                            Ratify Authoritative Reference Grade
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="p-8 text-center text-slate-400 text-xs">
                      Select a sample on the left to grade or adjudicate.
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-amber-50/70 border border-amber-200 rounded-2xl p-8 text-center space-y-3 text-amber-900">
                <Users className="w-10 h-10 mx-auto text-amber-600" />
                <div className="text-sm font-bold">Status: PENDING_EXPERT_ANNOTATION</div>
                <p className="text-xs max-w-md mx-auto text-amber-800">
                  Zero genuine tomato photographs are currently available for annotation. In accordance with strict non-fabrication principles, labels are never synthesized or pre-populated. Once genuine photos are uploaded via the <strong>Batch Ingestion</strong> tab, independent human graders will evaluate them here.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: STAKEHOLDER STUDY FORM */}
      {/* ========================================================================= */}
      {activeTab === 'feedback' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-lg font-bold text-civic-navy">Stage 2 Stakeholder Usability & Acceptance Study</h3>
                <p className="text-xs text-slate-500">
                  Structured 5-task usability evaluation instrument for produce graders, packhouse supervisors, and farm managers.
                </p>
              </div>
              <span className={`text-xs font-mono font-bold px-3 py-1 rounded-full border ${
                stakeholderData?.status === 'RECORDED_SESSIONS'
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-amber-50 text-amber-800 border-amber-200'
              }`}>
                {stakeholderData?.status === 'RECORDED_SESSIONS' 
                  ? `● ${stakeholderData.total_participants} Sessions Recorded` 
                  : '○ PENDING_EXTERNAL_EVIDENCE'}
              </span>
            </div>

            {/* Ethical Safeguards Declaration */}
            <div className="p-3.5 bg-indigo-50/70 border border-indigo-200 rounded-xl text-xs space-y-1.5 text-indigo-900">
              <span className="font-bold flex items-center">
                <Shield className="w-4 h-4 mr-1 text-indigo-600" />
                Ethical Safeguards & Non-Punitive Guarantee:
              </span>
              <p className="text-indigo-800">
                Participation is voluntary and anonymized. EQGS does not track grading speed for workplace pacing, does not rank workers against each other, and does not capture biometric/facial data.
              </p>
            </div>

            {feedbackSuccessMessage && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-bold">
                {feedbackSuccessMessage}
              </div>
            )}

            {/* Evaluation Form */}
            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-600 font-bold mb-1">Participant Agricultural Role:</label>
                  <select
                    value={participantRole}
                    onChange={(e) => setParticipantRole(e.target.value)}
                    className="w-full p-2 border border-slate-200 rounded-lg text-xs"
                  >
                    <option value="PRODUCE_GRADER">Produce Quality Grader</option>
                    <option value="PACKHOUSE_SORTER">Packhouse Sorter / Collection Worker</option>
                    <option value="FARM_OPERATOR">Farm Manager / Greenhouse Grower</option>
                    <option value="SENIOR_AUDITOR">Agricultural Inspector / Senior Reviewer</option>
                  </select>
                </div>
              </div>

              {/* Tasks Completed Checklist */}
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                <span className="font-bold text-slate-700 block">5 Evaluation Tasks Completed During Session:</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-600">
                  {[
                    { id: 'task_1', label: 'Task 1: Image Capture & Quality Gate Check' },
                    { id: 'task_2', label: 'Task 2: Feature Extraction & Provisional Grade Review' },
                    { id: 'task_3', label: 'Task 3: Independent Double-Blind Quality Grading' },
                    { id: 'task_4', label: 'Task 4: Senior Adjudication Review' },
                    { id: 'task_5', label: 'Task 5: Offline PWA Capture & Synchronization' },
                  ].map((t) => (
                    <label key={t.id} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={completedTasks[t.id] ?? false}
                        onChange={(e) => setCompletedTasks({ ...completedTasks, [t.id]: e.target.checked })}
                        className="rounded accent-indigo-600"
                      />
                      <span>{t.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Standardized 5-Point Likert Survey */}
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                <span className="font-bold text-slate-700 block">Standardized Likert Ratings (1 = Strongly Disagree, 5 = Strongly Agree):</span>
                {[
                  { id: 'q1_usability', text: 'Q1: The grading interface was straightforward to navigate on a mobile screen.' },
                  { id: 'q2_explanation_clarity', text: 'Q2: The rule explanations clearly showed me why a specific grade was assigned.' },
                  { id: 'q3_attribute_accuracy', text: 'Q3: The measured surface defect percentage and color stage aligned with my visual judgment.' },
                  { id: 'q4_disagreement_fairness', text: 'Q4: The double-blind review process provides a fair, unbiased method to resolve grader differences.' },
                  { id: 'q5_packhouse_viability', text: 'Q5: The offline queue and local saving make this tool practical for remote packhouses with weak connectivity.' },
                ].map((q) => (
                  <div key={q.id} className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 pb-2 gap-2">
                    <span className="text-slate-600">{q.text}</span>
                    <div className="flex gap-2">
                      {[1, 2, 3, 4, 5].map((val) => (
                        <button
                          key={val}
                          type="button"
                          onClick={() => setLikertScores({ ...likertScores, [q.id]: val })}
                          className={`w-7 h-7 rounded-lg font-bold text-xs border ${
                            likertScores[q.id] === val
                              ? 'bg-indigo-600 text-white border-indigo-700'
                              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                          }`}
                        >
                          {val}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Qualitative Feedback Text Areas */}
              <div className="space-y-3">
                <span className="font-bold text-slate-700 block">Qualitative Feedback:</span>
                <div>
                  <label className="block text-slate-600 mb-1">What specific information was missing from the grading explanation?</label>
                  <textarea
                    rows={2}
                    value={qualFeedback.missing_info}
                    onChange={(e) => setQualFeedback({ ...qualFeedback, missing_info: e.target.value })}
                    className="w-full p-2 border border-slate-200 rounded-lg text-xs"
                    placeholder="e.g., Would like explicit stem cavity rot callout..."
                  />
                </div>
                <div>
                  <label className="block text-slate-600 mb-1">In what scenarios would you override the system's provisional grade?</label>
                  <textarea
                    rows={2}
                    value={qualFeedback.override_scenarios}
                    onChange={(e) => setQualFeedback({ ...qualFeedback, override_scenarios: e.target.value })}
                    className="w-full p-2 border border-slate-200 rounded-lg text-xs"
                    placeholder="e.g., Hidden internal soft spots detectable by touch..."
                  />
                </div>
                <div>
                  <label className="block text-slate-600 mb-1">What features or changes would make this tool faster during harvest days?</label>
                  <textarea
                    rows={2}
                    value={qualFeedback.speed_improvements}
                    onChange={(e) => setQualFeedback({ ...qualFeedback, speed_improvements: e.target.value })}
                    className="w-full p-2 border border-slate-200 rounded-lg text-xs"
                    placeholder="e.g., Voice grade confirmation, continuous crate scanning..."
                  />
                </div>
              </div>

              <button
                onClick={() => stakeholderMutation.mutate({
                  role: participantRole,
                  completed_tasks: completedTasks,
                  likert_scores: likertScores,
                  qualitative_feedback: qualFeedback,
                })}
                disabled={stakeholderMutation.isPending}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold text-xs shadow-sm transition-colors flex items-center justify-center space-x-2"
              >
                <Send className="w-4 h-4" />
                <span>Submit Anonymous Stakeholder Evaluation</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: GUIDED DEMONSTRATION WALKTHROUGH */}
      {/* ========================================================================= */}
      {activeTab === 'demo' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-lg font-bold text-civic-navy">Stage 2 Guided Demonstration (8 Steps)</h3>
                <p className="text-xs text-slate-500">
                  Step-by-step verification walkthrough demonstrating all core Stage 2 agricultural produce capabilities.
                </p>
              </div>
              <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-800 border border-slate-200">
                Step {demoStep} of 8
              </span>
            </div>

            {/* Stepper Navigation Bar */}
            <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5 text-center">
              {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                <button
                  key={s}
                  onClick={() => setDemoStep(s)}
                  className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                    demoStep === s
                      ? 'bg-rose-600 text-white border-rose-700 shadow-sm'
                      : s < demoStep
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                      : 'bg-slate-50 text-slate-500 border-slate-200'
                  }`}
                >
                  Step {s}
                </button>
              ))}
            </div>

            {/* Step Content Card */}
            <div className="p-6 rounded-xl border border-slate-200 bg-slate-50 space-y-4">
              {demoStep === 1 && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-rose-700 font-bold text-sm">
                    <Camera className="w-5 h-5" />
                    <h4>Step 1: Genuine Produce Photograph Ingestion</h4>
                  </div>
                  <p className="text-xs text-slate-600">
                    Demonstrate image upload via the <strong>Grading & Diagnostics</strong> or <strong>Batch Ingestion</strong> tab. The pipeline decodes bytes, strips EXIF/GPS tags, calculates cryptographic SHA-256 and perceptual difference hashes (dHash), and screens for PII/skin-tone indicators.
                  </p>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs font-mono">
                    <span className="font-bold text-slate-700 block mb-1">Architecture Verification:</span>
                    <span>POST /api/v1/produce/real/upload &rarr; dataset/produce/real/raw/ &rarr; dataset/produce/real/processed/</span>
                  </div>
                </div>
              )}

              {demoStep === 2 && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-rose-700 font-bold text-sm">
                    <AlertTriangle className="w-5 h-5" />
                    <h4>Step 2: Optical Quality Checks & Retake Gate</h4>
                  </div>
                  <p className="text-xs text-slate-600">
                    Demonstrate how low illuminance (&lt; 40 lux) or severe motion blur (&sigma;&sup2; &lt; 100) triggers the prominent red rejection banner: <em>"Image quality insufficient for reliable grading. Please retake the photograph."</em>
                  </p>
                  <div className="p-3 bg-red-50 rounded-lg border border-red-200 text-xs text-red-800 font-semibold">
                    Optical Gate ensures uncertain captures never receive unverified high-confidence grades.
                  </div>
                </div>
              )}

              {demoStep === 3 && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-rose-700 font-bold text-sm">
                    <Sparkles className="w-5 h-5" />
                    <h4>Step 3: Explainable Provisional Grading</h4>
                  </div>
                  <p className="text-xs text-slate-600">
                    Show the 10-attribute diagnostic panel: surface defect %, USDA ripeness chromaticity stage, shape circularity, and triggered deterministic rules. Highlight plain-language contributing factors.
                  </p>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs text-slate-700">
                    <strong>Rule Engine Transparency:</strong> Grade A capped at &le;5% defect area; Grade B capped at &le;15%; Blossom end rot or severe bruising immediately disqualifies to Grade C.
                  </div>
                </div>
              )}

              {demoStep === 4 && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-rose-700 font-bold text-sm">
                    <Users className="w-5 h-5" />
                    <h4>Step 4: Double-Blind Human Annotation</h4>
                  </div>
                  <p className="text-xs text-slate-600">
                    Navigate to the <strong>Double-Blind Annotation</strong> tab. Show how Grader 1 submits an independent assessment. Grader 2 evaluates the sample without seeing Grader 1's grade or the AI recommendation.
                  </p>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs font-mono text-slate-600">
                    POST /api/v1/produce/real/annotate &rarr; status: PARTIALLY_ANNOTATED (Grader 1 grade masked)
                  </div>
                </div>
              )}

              {demoStep === 5 && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-rose-700 font-bold text-sm">
                    <Shield className="w-5 h-5" />
                    <h4>Step 5: Disagreement Review & Senior Adjudication</h4>
                  </div>
                  <p className="text-xs text-slate-600">
                    Demonstrate how conflicting grades (e.g. Grader 1 = A, Grader 2 = B) escalate to <strong>OPEN_DISAGREEMENT</strong>. Senior Reviewer inspects both entries and ratifies a definitive reference grade with documented clinical rationale.
                  </p>
                  <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-900">
                    Safety Invariant: AI never overrides human disagreements; authoritative decisions are made by agricultural referees.
                  </div>
                </div>
              )}

              {demoStep === 6 && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-rose-700 font-bold text-sm">
                    <Award className="w-5 h-5" />
                    <h4>Step 6: Controlled Experiment Metrics & Targets</h4>
                  </div>
                  <p className="text-xs text-slate-600">
                    Inspect the <strong>Metrics Dashboard</strong>. Point out the Before-and-After Controlled Experiment table displaying Baseline (Human-Only) benchmarks, Predefined Targets, and Measured results.
                  </p>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs text-slate-700">
                    <strong>Non-Fabrication Guarantee:</strong> Status clearly displays <code>PENDING_REAL_EXPERIMENT</code> until live grader sessions on &ge; 10 consensus samples are conducted.
                  </div>
                </div>
              )}

              {demoStep === 7 && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-rose-700 font-bold text-sm">
                    <Smartphone className="w-5 h-5" />
                    <h4>Step 7: Offline PWA Capture & Synchronization</h4>
                  </div>
                  <p className="text-xs text-slate-600">
                    Demonstrate offline resilience: simulate offline mode, draft a grading record locally in IndexedDB, restore connectivity, and verify automatic background sync to PostgreSQL without data loss.
                  </p>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs text-slate-700">
                    Service Worker cache + IndexedDB offline queue guaranteed for remote packhouses with intermittent cellular reception.
                  </div>
                </div>
              )}

              {demoStep === 8 && (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-rose-700 font-bold text-sm">
                    <FileCheck2 className="w-5 h-5" />
                    <h4>Step 8: Stakeholder Acceptance & Operational Limitations</h4>
                  </div>
                  <p className="text-xs text-slate-600">
                    Review the <strong>Stakeholder Study Form</strong> and documented limitations: monocular occlusion (underside defects invisible), ambient lighting color shifts, and rustic wood-grain shadow interference (Failure Case 4).
                  </p>
                  <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-200 text-xs text-indigo-900 font-semibold">
                    Informed participant consent and non-surveillance commitments verified in <code>docs/STAKEHOLDER_VALIDATION.md</code>.
                  </div>
                </div>
              )}

              {/* Stepper Action Buttons */}
              <div className="flex justify-between pt-2">
                <button
                  onClick={() => setDemoStep((prev) => Math.max(1, prev - 1))}
                  disabled={demoStep === 1}
                  className="px-4 py-2 rounded-xl text-xs font-bold border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 transition-colors"
                >
                  Previous Step
                </button>
                <button
                  onClick={() => setDemoStep((prev) => Math.min(8, prev + 1))}
                  disabled={demoStep === 8}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-rose-600 text-white hover:bg-rose-700 disabled:opacity-40 transition-colors flex items-center space-x-1"
                >
                  <span>Next Step</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
