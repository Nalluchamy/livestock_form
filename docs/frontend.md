# ELHGS Frontend Documentation

The Explainable Livestock Health Grading System frontend is built with React 19, Vite, TypeScript, and TailwindCSS. It is designed mobile-first for outdoor field usage with large tap targets and high contrast.

## Tech Stack
- **Framework:** React 19 + Vite
- **Language:** TypeScript (Strict Mode)
- **Styling:** TailwindCSS (Civic Color Palette: Navy, Teal, Emerald, Amber, Rose)
- **State & Data Fetching:** TanStack Query v5
- **Form Management & Validation:** React Hook Form + Zod
- **Routing:** React Router v6

---

## Folder Structure

```
frontend/src/
├── assets/          # Static assets & icons
├── components/      # Reusable UI components
│   ├── AppHeader.tsx
│   ├── AttributeForm.tsx
│   ├── BottomNavigation.tsx
│   ├── ConfidenceBar.tsx
│   ├── ExplanationPanel.tsx
│   ├── GradeBadge.tsx
│   ├── ImageUploader.tsx
│   ├── KpiCard.tsx
│   ├── Sidebar.tsx
│   └── ...
├── layouts/         # Root app layout wrapper
│   └── RootLayout.tsx
├── pages/           # Application views
│   ├── Home.tsx
│   ├── CaptureGrade.tsx
│   ├── GradingResult.tsx
│   ├── GradingHistory.tsx
│   ├── DisagreementReview.tsx
│   ├── MetricsDashboard.tsx
│   └── EthicsLimitations.tsx
├── routes/          # Browser router configuration
├── services/        # Axios API clients
│   ├── api.ts
│   ├── gradingService.ts
│   ├── metricsService.ts
│   └── ...
└── types/           # TypeScript interfaces & types
```

---

## Features & Responsive Strategy

1. **Mobile-First Layout:**
   - On small screens (< 768px), navigation collapses to a fixed `BottomNavigation` bar with large touch targets.
   - On desktop (>= 768px), a fixed left `Sidebar` provides expanded navigation links.

2. **Attribute Form Validation:**
   - Validates Body Condition Score (1.0 - 5.0) via Zod schemas before firing HTTP requests.
   - Converts technical inputs into friendly dropdown choices for fast, low-error field entry.

3. **Explainability & Disagreement UI:**
   - Displays real-time confidence scores and lists exact rule decisions (e.g., Critical Failures vs. Passed rules).
   - Flagging human disagreements notifies users that the AI **never** overrides human authority.

---

## Running Locally

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start dev server:
   ```bash
   npm run dev
   ```
   The application will be accessible at `http://localhost:3000` and automatically proxy `/api` calls to `http://localhost:8000`.
