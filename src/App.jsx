import { useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  BookOpenCheck,
  BrainCircuit,
  Check,
  ChevronRight,
  CircleDollarSign,
  ClipboardList,
  FileText,
  Gamepad2,
  GraduationCap,
  HelpCircle,
  LineChart,
  Lock,
  Megaphone,
  MoreVertical,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Target,
  UsersRound,
} from "lucide-react";

import { apiGet, apiPost } from "./api";
import { computeFinance, steps } from "./demoLogic";
import Logo from "../src/Logo.png";
import BLogo from "../src/xamklogo.png";

const socialImage = "/generated_assets/social_designed_1777373144.png";
const brochureImage = "/generated_assets/brochure_designed_1777373132.png";

const stepIcons = {
  home: LineChart,
  match: Target,
  summary: BrainCircuit,
  programme: ClipboardList,
  personalized: GraduationCap,
  teacher: UsersRound,
  marketing: Megaphone,
  income: CircleDollarSign,
};

const trendIcons = {
  "Game Development": Gamepad2,
  "Ethical Hacking": ShieldCheck,
  "Data Science": BarChart3,
  "Digital Marketing": Megaphone,
};

const keywordTone = ["blue", "purple", "pink", "green", "teal", "violet"];

const outcomeTemplates = [
  "Apply {domain} concepts to solve a practical {course} challenge from brief to presentation.",
  "Build a portfolio-ready {domain} artefact that demonstrates planning, implementation, testing, and reflection.",
  "Evaluate {domain} solutions using clear criteria, feedback, and evidence from real learner or stakeholder needs.",
  "Communicate {domain} decisions in a concise format for non-specialist stakeholders and peer review.",
  "Use {keywords} to connect the source course content with a current short-programme opportunity.",
  "Design an ethical and accessible {domain} workflow that can be adapted for professional practice.",
];

const weekTopicTemplates = {
  1: [
    "{domain} Foundations - Mapping core concepts, tools, and terminology through guided examples",
    "Readiness Lab - Preparing source materials and documenting assumptions for {course}",
    "Starter Workflow - Reproducing a simple end-to-end task with instructor feedback",
    "Context Sprint - Connecting {keywords} to learner needs and industry examples",
  ],
  2: [
    "Applied Studio - Building and comparing practical {domain} solutions with peer feedback",
    "Evaluation Lab - Testing outputs against clear success criteria and improving decisions",
    "Case Challenge - Applying {course} methods to a realistic short-programme scenario",
    "Storytelling Sprint - Turning technical work into stakeholder-ready recommendations",
  ],
  3: [
    "Prototype Sprint - Combining weekly skills into a working learner-facing project",
    "Iteration Clinic - Using feedback, testing, and evidence to improve the project",
    "Advanced Practice - Extending {domain} work with {keywords} and independent choices",
    "Portfolio Workshop - Packaging progress into a clear professional artefact",
  ],
  default: [
    "Capstone Build - Completing a polished {domain} project with documented decisions",
    "Showcase Review - Presenting outcomes, trade-offs, and next steps to peers",
    "Implementation Clinic - Refining the final work against assessment criteria",
    "Reflection Lab - Connecting the finished project to future study or work practice",
  ],
};

function App() {
  const [bootstrap, setBootstrap] = useState({
    trends: [],
    teachers: [],
    provider: { name: "AI", hasKey: false, model: "" },
  });
  const [selectedTrendName, setSelectedTrendName] = useState("");
  const [activeStep, setActiveStep] = useState("home");
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState("");
  const [notice, setNotice] = useState(null);
  const [imagePaths, setImagePaths] = useState({});
  const [brochure, setBrochure] = useState("");
  const [emails, setEmails] = useState({});
  const [programmeApproach, setProgrammeApproach] = useState("Project-first sprint");

  useEffect(() => {
    let alive = true;
    apiGet("/api/bootstrap")
      .then((data) => {
        if (!alive) return;
        setBootstrap(data);
        setSelectedTrendName((current) => current || data.trends?.[0]?.trend || "");
      })
      .catch((error) => {
        if (!alive) return;
        setNotice({ type: "error", text: `Could not load backend data: ${error.message}` });
      });

    return () => {
      alive = false;
    };
  }, []);

  const selectedTrend = useMemo(
    () => bootstrap.trends.find((trend) => trend.trend === selectedTrendName) || bootstrap.trends[0],
    [bootstrap.trends, selectedTrendName],
  );

  const activeIndex = steps.findIndex((step) => step.id === activeStep);
  const selectedStep = steps[activeIndex] || steps[0];
  const provider = plan?.provider || bootstrap.provider;
  const planGenerated = Boolean(plan);

  function selectTrend(name) {
    setSelectedTrendName(name);
    setPlan(null);
    setImagePaths({});
    setBrochure("");
    setEmails({});
    setNotice(null);
    setActiveStep("home");
  }

  function navigate(id) {
    if (id === "home" || planGenerated) {
      setActiveStep(id);
    }
  }

  async function runAction(label, action) {
    setLoading(label);
    setNotice(null);
    try {
      await action();
    } catch (error) {
      setNotice({ type: "error", text: error.message });
    } finally {
      setLoading("");
    }
  }

  async function generatePlan() {
    await runAction("Generating course plan with AI", async () => {
      const nextPlan = await apiPost("/api/plan", { trend_name: selectedTrendName });
      setPlan(nextPlan);
      setNotice({
        type: "success",
        text: nextPlan.provider?.hasKey
          ? `Course plan generated with ${nextPlan.provider.name}.`
          : "Course plan generated with offline fallback content.",
      });
    });
  }

  async function regenerateSummary() {
    if (!plan) return;
    await runAction("Regenerating summary with AI", async () => {
      const data = await apiPost("/api/regenerate-summary", { plan });
      setPlan((current) => ({
        ...current,
        summary: data.summary,
        summaryUsedFallback: data.summaryUsedFallback,
        difficulty: data.difficulty,
        market: data.market,
        personalized: data.personalized,
        provider: data.provider,
      }));
      setNotice({
        type: data.summaryUsedFallback ? "warning" : "success",
        text: data.summaryUsedFallback
          ? data.message || "Summary regeneration used fallback content."
          : `Summary regenerated with ${data.provider.name}.`,
      });
    });
  }

  async function regenerateProgramme(approach = "") {
    if (!plan) return;
    await runAction("Regenerating programme with AI", async () => {
      const data = await apiPost("/api/regenerate-programme", { plan, approach });
      setPlan((current) => ({
        ...current,
        programme: data.programme,
        programmeUsedFallback: data.programmeUsedFallback,
        provider: data.provider,
      }));
      setNotice({
        type: data.programmeUsedFallback ? "warning" : "success",
        text: data.programmeUsedFallback
          ? data.message || "Programme regeneration used fallback content."
          : approach
            ? `Programme regenerated with ${data.provider.name} using a ${approach} approach.`
            : `Programme regenerated with ${data.provider.name}.`,
      });
    });
  }

  function updateProgramme(nextProgramme) {
    setPlan((current) => ({
      ...current,
      programme: nextProgramme,
    }));
  }

  async function regeneratePersonalization() {
    if (!plan) return;
    await runAction("Regenerating personalized learning with AI", async () => {
      const data = await apiPost("/api/regenerate-personalization", { plan });
      setPlan((current) => ({
        ...current,
        personalized: data.personalized,
        provider: data.provider,
      }));
      setNotice({
        type: data.personalized.usedFallback ? "warning" : "success",
        text: data.personalized.usedFallback
          ? data.message || "Personalized learning used fallback content."
          : `Personalized learning regenerated with ${data.provider.name}.`,
      });
    });
  }

  async function regenerateQuestion(index, chapter) {
    if (!plan) return;
    await runAction("Regenerating mini-game question with AI", async () => {
      const data = await apiPost("/api/regenerate-question", {
        course_name: plan.course.course_name,
        student_field: "nursing",
        chapter,
      });
      if (!data.ok) {
        setNotice({ type: "error", text: data.message });
        return;
      }
      setPlan((current) => {
        const chapters = [...current.personalized.chapters];
        chapters[index] = data.chapter;
        return {
          ...current,
          personalized: { ...current.personalized, chapters },
          provider: data.provider,
        };
      });
      setNotice({ type: "success", text: data.message });
    });
  }

  function updateChapter(index, nextChapter) {
    setPlan((current) => {
      const chapters = [...current.personalized.chapters];
      chapters[index] = nextChapter;
      return {
        ...current,
        personalized: { ...current.personalized, chapters },
      };
    });
  }

  function updateFinalAssignment(value) {
    setPlan((current) => ({
      ...current,
      personalized: { ...current.personalized, finalAssignment: value },
    }));
  }

  async function regenerateMarketing() {
    if (!plan) return;
    await runAction("Regenerating marketing copy with AI", async () => {
      const data = await apiPost("/api/regenerate-marketing", { plan });
      setPlan((current) => ({ ...current, marketing: data.marketing, provider: data.provider }));
      setNotice({
        type: data.marketing.usedFallback ? "warning" : "success",
        text: data.marketing.usedFallback
          ? data.message || "Marketing regeneration used fallback content."
          : `Marketing copy regenerated with ${data.provider.name}.`,
      });
    });
  }

  async function generateMarketingImage(imageType) {
    if (!plan) return;
    await runAction(`Generating ${imageType} image with Gemini`, async () => {
      const data = await apiPost("/api/generate-marketing-image", {
        programme_title: plan.programme.title,
        content: plan.marketing,
        image_type: imageType,
      });
      if (!data.ok) {
        setNotice({ type: "error", text: data.message });
        return;
      }
      setImagePaths((current) => ({
        ...current,
        [imageType]: `${data.imageUrl}?t=${Date.now()}`,
      }));
      setPlan((current) => ({ ...current, provider: data.provider }));
      setNotice({ type: "success", text: data.message });
    });
  }

  async function generateBrochure() {
    if (!plan) return;
    await runAction("Generating brochure text with AI", async () => {
      const data = await apiPost("/api/generate-brochure", {
        programme: plan.programme,
        course: plan.course,
        analysis: plan.analysis,
      });
      setBrochure(data.brochure);
      setPlan((current) => ({ ...current, provider: data.provider }));
      setNotice({
        type: data.ok ? "success" : "error",
        text: data.ok ? `Brochure generated with ${data.provider.name}.` : data.message || "Brochure generation failed.",
      });
    });
  }

  async function searchTalent() {
    if (!plan) return;
    await runAction("Searching recruitment talent pools", async () => {
      const data = await apiPost("/api/search-talent", { plan });
      setPlan((current) => ({
        ...current,
        talent: data.talent,
        talentStatus: data.talentStatus,
      }));
      setNotice({ type: "success", text: data.talentStatus });
    });
  }

  async function generateEmail(candidate) {
    if (!plan) return;
    await runAction("Generating recruitment email with AI", async () => {
      const data = await apiPost("/api/generate-recruitment-email", {
        candidate,
        programme: plan.programme,
        course: plan.course,
      });
      const id = candidate.talent_id || candidate.name;
      setEmails((current) => ({
        ...current,
        [id]: { text: data.email, usedFallback: data.usedFallback },
      }));
      setPlan((current) => ({ ...current, provider: data.provider }));
      setNotice({
        type: data.usedFallback ? "warning" : "success",
        text: data.usedFallback ? "Email generated from fallback template." : `Email generated with ${data.provider.name}.`,
      });
    });
  }

  return (
    <div className="app-shell">
      <Sidebar
        activeStep={activeStep}
        activeIndex={Math.max(activeIndex, 0)}
        onNavigate={navigate}
        planGenerated={planGenerated}
        provider={provider}
      />

      <main className="workspace">
        <TopBar provider={provider} />
        <section className="stage" aria-labelledby="screen-title">
          {notice && <Notice notice={notice} onDismiss={() => setNotice(null)} />}
          {loading && <LoadingBanner label={loading} />}

          {activeStep === "home" && (
            <HomeScreen
              trends={bootstrap.trends}
              selectedTrend={selectedTrend}
              selectedTrendName={selectedTrendName}
              onSelectTrend={selectTrend}
              onGeneratePlan={generatePlan}
              planGenerated={planGenerated}
              onOpenPlan={() => navigate("match")}
              loading={loading}
            />
          )}

          {activeStep !== "home" && !planGenerated && <LockedScreen step={selectedStep} />}

          {activeStep === "match" && planGenerated && <CourseMatchScreen plan={plan} />}
          {activeStep === "summary" && planGenerated && (
            <SummaryScreen plan={plan} onRegenerate={regenerateSummary} loading={loading} />
          )}
          {activeStep === "programme" && planGenerated && (
            <ProgrammeScreen
              plan={plan}
              approach={programmeApproach}
              onApproachChange={setProgrammeApproach}
              onProgrammeChange={updateProgramme}
              onRegenerate={regenerateProgramme}
              loading={loading}
            />
          )}
          {activeStep === "personalized" && planGenerated && (
            <PersonalizedScreen
              plan={plan}
              onRegenerate={regeneratePersonalization}
              onRegenerateQuestion={regenerateQuestion}
              onChapterChange={updateChapter}
              onFinalAssignmentChange={updateFinalAssignment}
              loading={loading}
            />
          )}
          {activeStep === "teacher" && planGenerated && (
            <TeacherScreen
              plan={plan}
              emails={emails}
              onSearchTalent={searchTalent}
              onGenerateEmail={generateEmail}
              loading={loading}
            />
          )}
          {activeStep === "marketing" && planGenerated && (
            <MarketingScreen
              plan={plan}
              imagePaths={imagePaths}
              brochure={brochure}
              onRegenerateMarketing={regenerateMarketing}
              onGenerateImage={generateMarketingImage}
              onGenerateBrochure={generateBrochure}
              loading={loading}
            />
          )}
          {activeStep === "income" && planGenerated && <IncomeScreen plan={plan} />}
        </section>
      </main>
    </div>
  );
}

function programmeDomain(plan) {
  return plan.trend?.trend || plan.programme?.basedOn || plan.course?.course_name || "the topic";
}

function programmeCourseName(plan) {
  return plan.course?.course_name || plan.programme?.basedOn || "the source course";
}

function programmeKeywords(plan) {
  const keywords = plan.trend?.keywords?.length ? plan.trend.keywords : plan.course?.keywords || [];
  return keywords.slice(0, 3).join(", ") || programmeDomain(plan).toLowerCase();
}

function fillSuggestionTemplate(template, plan) {
  return template
    .replaceAll("{domain}", programmeDomain(plan))
    .replaceAll("{course}", programmeCourseName(plan))
    .replaceAll("{keywords}", programmeKeywords(plan));
}

function weekNumber(weekLabel) {
  const match = String(weekLabel).match(/\d+/);
  return match ? Number(match[0]) : 0;
}

function uniqueSuggestions(items, currentValue = "", limit = 4) {
  const current = currentValue.trim().toLowerCase();
  const seen = new Set();
  return items
    .map((item) => item.trim())
    .filter(Boolean)
    .filter((item) => {
      const key = item.toLowerCase();
      if (key === current || seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .slice(0, limit);
}

function outcomeSuggestions(plan, index, currentValue) {
  const rotated = [...outcomeTemplates.slice(index), ...outcomeTemplates.slice(0, index)];
  return uniqueSuggestions(rotated.map((template) => fillSuggestionTemplate(template, plan)), currentValue, 4);
}

function topicSuggestions(plan, weekLabel, index, currentValue) {
  const templates = weekTopicTemplates[weekNumber(weekLabel)] || weekTopicTemplates.default;
  const rotated = [...templates.slice(index), ...templates.slice(0, index), ...weekTopicTemplates.default];
  return uniqueSuggestions(rotated.map((template) => fillSuggestionTemplate(template, plan)), currentValue, 4);
}

function SuggestionOptions({ label, options, onSelect }) {
  if (!options.length) return null;
  return (
    <div className="suggestion-panel">
      <span>{label}</span>
      <div className="suggestion-options">
        {options.map((option) => (
          <button type="button" key={option} onClick={() => onSelect(option)}>
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}

function Sidebar({ activeStep, activeIndex, onNavigate, planGenerated, provider }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <img src={BLogo} alt="Logo"  className="w-50"/>
      </div>

      <div className="ai-status">
        <span className={provider?.hasKey ? "status-dot" : "status-dot missing"} />
        <div>
          <strong>{provider?.hasKey ? `${provider.name} key loaded` : "No AI key loaded"}</strong>
          <small>{provider?.model || (provider?.hasKey ? "Server-side .env" : "Offline fallback ready")}</small>
        </div>
      </div>

      <nav className="progress-nav" aria-label="Demo sections">
        <p className="nav-eyebrow">Your Progress</p>
        {steps.map((step, index) => {
          const Icon = stepIcons[step.id];
          const locked = !planGenerated && step.id !== "home";
          const active = activeStep === step.id;

          return (
            <button
              className={`nav-item ${active ? "active" : ""}`}
              key={step.id}
              type="button"
              disabled={locked}
              aria-current={active ? "page" : undefined}
              onClick={() => onNavigate(step.id)}
            >
              <span className="nav-index">{locked ? <Lock size={13} /> : index + 1}</span>
              <Icon size={15} aria-hidden="true" />
              <span>{step.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-foot">
        <span>
          Step {activeIndex + 1} of {steps.length}
        </span>
        <div className="progress-track">
          <span style={{ width: `${((activeIndex + 1) / steps.length) * 100}%` }} />
        </div>
      </div>
    </aside>
  );
}

function TopBar({ provider }) {
  return (
    <header className="topbar">
      <div className="topbar-title">
        <img src={BLogo} alt="Logo"  className="w-20"/>
        
        <span>Turning Xamk courses into trend-based year-round short programmes</span>
      </div>
      <div className="topbar-meta">{provider?.hasKey ? `${provider.name} AI enabled` : "Fallback mode"}</div>
      <div className="topbar-actions">
        <IconButton label="Help" icon={HelpCircle} />
        <IconButton label="More options" icon={MoreVertical} />
      </div>
    </header>
  );
}

function Notice({ notice, onDismiss }) {
  return (
    <div className={`notice ${notice.type}`}>
      <span>{notice.text}</span>
      <button type="button" onClick={onDismiss} aria-label="Dismiss notice">
        x
      </button>
    </div>
  );
}

function LoadingBanner({ label }) {
  return (
    <div className="loading-banner">
      <RefreshCw size={16} />
      <span>{label}...</span>
    </div>
  );
}

function HomeScreen({ trends, selectedTrend, selectedTrendName, onSelectTrend, onGeneratePlan, planGenerated, onOpenPlan, loading }) {
  return (
    <div className="screen-grid home-screen">
      <div className="screen-main">
        <ScreenHeader title="Trending Topics" description="Select a trend to explore and generate a course plan." />

        <div className="topic-grid">
          {trends.map((trend) => (
            <TopicCard
              key={trend.trend}
              trend={trend}
              selected={trend.trend === selectedTrendName}
              onSelect={() => onSelectTrend(trend.trend)}
            />
          ))}
        </div>

        {selectedTrend && (
          <div className="selected-row">
            <SelectedTrendPanel trend={selectedTrend} />
            <NextStepPanel planGenerated={planGenerated} />
          </div>
        )}

        <button className="primary-cta" type="button" disabled={Boolean(loading)} onClick={planGenerated ? onOpenPlan : onGeneratePlan}>
          {planGenerated ? <Check size={17} /> : <Sparkles size={17} />}
          {planGenerated ? "Open Course Match" : "Generate Course Plan"}
        </button>
      </div>
    </div>
  );
}

function TopicCard({ trend, selected, onSelect }) {
  const Icon = trendIcons[trend.trend] || LineChart;

  return (
    <article className={`topic-card ${selected ? "selected" : ""}`}>
      <div className="topic-icon">
        <Icon size={25} aria-hidden="true" />
      </div>
      <h3>{trend.trend}</h3>
      <StatusChip status={trend.status} />
      <div className="topic-divider" />
      <span className="score-label">Score</span>
      <strong className="topic-score">{trend.score}</strong>
      <button className={selected ? "selected-button" : "select-button"} type="button" onClick={onSelect}>
        {selected && <Check size={14} />}
        {selected ? "Selected" : "Select"}
      </button>
    </article>
  );
}

function SelectedTrendPanel({ trend }) {
  const Icon = trendIcons[trend.trend] || LineChart;

  return (
    <article className="selected-panel">
      <div className="selected-icon">
        <Icon size={28} aria-hidden="true" />
      </div>
      <div className="selected-copy">
        <h3>Selected: {trend.trend}</h3>
        <p>
          <strong>Reason:</strong> {trend.reason}
        </p>
        <div className="chip-row" aria-label="Selected trend keywords">
          {trend.keywords.map((keyword, index) => (
            <KeywordChip key={keyword} tone={keywordTone[index % keywordTone.length]}>
              {keyword}
            </KeywordChip>
          ))}
        </div>
      </div>
    </article>
  );
}

function NextStepPanel({ planGenerated }) {
  return (
    <article className="next-panel">
      <div className="next-header">
        <span className="target-ring">
          <Target size={22} aria-hidden="true" />
        </span>
        <div>
          <h3>What is next?</h3>
          <p>Match this trend with the best Xamk course to build your short programme.</p>
        </div>
      </div>
      <div className="next-step">
        <span>2</span>
        <div>
          <strong>{planGenerated ? "Course matching ready" : "Next step: Course matching"}</strong>
          <p>Find the right source course and material fit.</p>
        </div>
      </div>
    </article>
  );
}

function CourseMatchScreen({ plan }) {
  return (
    <div className="content-stack">
      <ScreenHeader title="Course Match" description="Trend signal matched to an existing Xamk course." />

      <div className="two-column">
        <InfoPanel icon={LineChart} label="Selected Trend" title={plan.trend.trend}>
          <ChipList items={plan.trend.keywords} />
        </InfoPanel>
        <InfoPanel icon={BookOpenCheck} label="Matched Course" title={plan.course.course_name}>
          <p>{plan.course.description}</p>
        </InfoPanel>
      </div>

      <div className="match-strip">
        <div className="match-score">
          <span>{plan.match.score}%</span>
          <small>Match score</small>
        </div>
        <div>
          <h3>{plan.match.reason}</h3>
          <ChipList items={plan.match.matchingKeywords} />
        </div>
      </div>
    </div>
  );
}

function SummaryScreen({ plan, onRegenerate, loading }) {
  const market = plan.market || {};
  const difficulty = plan.difficulty || { level: "Medium", rationale: "Difficulty analysis is not available yet.", signals: [] };

  return (
    <div className="content-stack">
      <ScreenHeader title="AI Summary" description="Course material analysis with live AI regeneration." />
      <ActionRow
        label={plan.summaryUsedFallback ? "Using offline fallback summary" : `Generated by ${plan.provider?.name || "AI"}`}
        buttonLabel="Regenerate with AI"
        onClick={onRegenerate}
        disabled={Boolean(loading)}
      />

      <div className="summary-layout">
        <article className="summary-card">
          <div className="panel-label">
            <BrainCircuit size={16} />
            AI Summary
          </div>
          <h3>{plan.summary.title}</h3>
          <p>{plan.summary.body}</p>
          <ul className="clean-list">
            {plan.summary.highlights.map((item) => (
              <li key={item}>
                <Check size={15} />
                {item}
              </li>
            ))}
          </ul>
        </article>

        <article className="material-preview">
          <div className="panel-label">
            <FileText size={16} />
            Material Preview
          </div>
          <p>{plan.materialText.slice(0, 440)}...</p>
        </article>
      </div>

      <div className="insight-grid">
        <article className={`difficulty-card ${difficulty.level.toLowerCase()}`}>
          <span className="panel-label">AI Difficulty</span>
          <strong>{difficulty.level}</strong>
          <p>{difficulty.rationale}</p>
          <div className="chip-row">
            {(difficulty.signals || []).map((signal) => (
              <KeywordChip key={signal} tone="teal">
                {signal}
              </KeywordChip>
            ))}
          </div>
        </article>

        <article className="price-card">
          <span className="panel-label">Market Pricing</span>
          <div className="price-main">
            <strong>{formatEUR(market.recommendedPrice)}</strong>
            <span>Recommended Xamk price</span>
          </div>
          <p>{market.positioning}</p>
          <div className="price-stats">
            <MetricTile label="Competitor Avg" value={formatEUR(market.averageCompetitorPrice)} compact />
            <MetricTile label="Suggested Range" value={`${formatEUR(market.recommendedRange?.low)}-${formatEUR(market.recommendedRange?.high)}`} compact />
            <MetricTile label="Student Saves" value={formatEUR(market.priceDifference)} compact tone="good" />
          </div>
        </article>
      </div>

      <article className="market-table-card">
        <div className="copy-card-header">
          <span className="panel-label">Similar Programme Price Difference</span>
          <strong>{market.percentSaving || 0}% below market average</strong>
        </div>
        <div className="market-table">
          <div className="market-row header">
            <span>Other Platform</span>
            <span>Market Price</span>
            <span>CoursePilot Xamk</span>
            <span>Difference</span>
          </div>
          {(market.comparisonRows || []).map((row) => (
            <div className="market-row" key={`${row.provider}-${row.title}`}>
              <span>
                <strong>{row.provider}</strong>
                <small>{row.title}</small>
              </span>
              <span>{formatEUR(row.platformPrice)}</span>
              <span>{formatEUR(row.xamkPrice)}</span>
              <span className="saving">{formatEUR(row.difference)} less</span>
            </div>
          ))}
        </div>
      </article>

      <div className="metric-grid">
        <MetricTile label="Material Size" value={plan.analysis.size} />
        <MetricTile label="Recommended Duration" value={`${plan.analysis.weeks} weeks`} />
        <MetricTile label="Credits" value={`${plan.analysis.ects} ECTS`} />
        <MetricTile label="Word Count" value={plan.analysis.wordCount.toLocaleString()} />
      </div>
    </div>
  );
}

function ProgrammeScreen({ plan, approach, onApproachChange, onProgrammeChange, onRegenerate, loading }) {
  const programme = plan.programme;

  function patchProgramme(patch) {
    onProgrammeChange({ ...programme, ...patch });
  }

  function updateOutcome(index, value) {
    const outcomes = [...(programme.outcomes || [])];
    outcomes[index] = value;
    patchProgramme({ outcomes });
  }

  function addOutcome() {
    patchProgramme({ outcomes: [...(programme.outcomes || []), "New learning outcome"] });
  }

  function removeOutcome(index) {
    patchProgramme({ outcomes: (programme.outcomes || []).filter((_, itemIndex) => itemIndex !== index) });
  }

  function updateWeekTopic(week, index, value) {
    const weeklyStructure = { ...(programme.weeklyStructure || {}) };
    const topics = [...(weeklyStructure[week] || [])];
    topics[index] = value;
    weeklyStructure[week] = topics;
    patchProgramme({ weeklyStructure });
  }

  function addWeekTopic(week) {
    const weeklyStructure = { ...(programme.weeklyStructure || {}) };
    weeklyStructure[week] = [...(weeklyStructure[week] || []), "New topic - concrete activity students do"];
    patchProgramme({ weeklyStructure });
  }

  function removeWeekTopic(week, index) {
    const weeklyStructure = { ...(programme.weeklyStructure || {}) };
    weeklyStructure[week] = (weeklyStructure[week] || []).filter((_, itemIndex) => itemIndex !== index);
    patchProgramme({ weeklyStructure });
  }

  return (
    <div className="content-stack">
      <ScreenHeader title="Programme" description={programme.demoPitch || "Generated short programme plan."} />
      <ActionRow
        label={plan.programmeUsedFallback ? "Using offline fallback programme" : `Generated by ${plan.provider?.name || "AI"}`}
        buttonLabel="Regenerate Programme"
        onClick={() => onRegenerate()}
        disabled={Boolean(loading)}
      />

      <article className="approach-panel">
        <div>
          <span className="panel-label">Different AI Approach</span>
          <p>Regenerate the whole programme with a different curriculum angle while keeping the same selected course and market context.</p>
        </div>
        <div className="approach-controls">
          <select value={approach} onChange={(event) => onApproachChange(event.target.value)}>
            <option>Project-first sprint</option>
            <option>Beginner bootcamp</option>
            <option>Healthcare simulation pathway</option>
            <option>Business innovation launch</option>
            <option>Portfolio and career accelerator</option>
          </select>
          <button className="secondary-action" type="button" disabled={Boolean(loading)} onClick={() => onRegenerate(approach)}>
            <RefreshCw size={15} />
            Regenerate Different Approach
          </button>
        </div>
      </article>

      <article className="programme-hero">
        <div>
          <span className="panel-label">Generated Programme</span>
          <EditorInput value={programme.title} onChange={(value) => patchProgramme({ title: value })} />
          <EditorTextarea value={programme.targetStudents} onChange={(value) => patchProgramme({ targetStudents: value })} />
        </div>
        <div className="programme-facts">
          <label className="mini-editor">
            <span>Duration</span>
            <input
              type="number"
              min="1"
              max="8"
              value={programme.durationWeeks || 1}
              onChange={(event) => patchProgramme({ durationWeeks: Number(event.target.value) })}
            />
          </label>
          <label className="mini-editor">
            <span>Credits</span>
            <input
              type="number"
              min="1"
              max="10"
              value={programme.ects || 3}
              onChange={(event) => patchProgramme({ ects: Number(event.target.value) })}
            />
          </label>
          <label className="mini-editor">
            <span>Mode</span>
            <input value={programme.mode || ""} onChange={(event) => patchProgramme({ mode: event.target.value })} />
          </label>
        </div>
      </article>

      <div className="two-column">
        <InfoPanel icon={BookOpenCheck} label="Based On" title={programme.basedOn}>
          <label className="editor-label">
            Teacher
            <input className="editor-input small" value={programme.teacher || ""} onChange={(event) => patchProgramme({ teacher: event.target.value })} />
          </label>
          <ChipList items={programme.availableMonths} />
        </InfoPanel>
        <InfoPanel icon={Target} label="Assessment" title="Evidence of learning">
          <EditorTextarea value={programme.assessment || ""} onChange={(value) => patchProgramme({ assessment: value })} />
        </InfoPanel>
      </div>

      <article className="outcome-panel">
        <div className="copy-card-header">
          <h3>Learning Outcomes</h3>
          <button className="secondary-action" type="button" onClick={addOutcome}>
            Add Outcome
          </button>
        </div>
        <div className="programme-editor-list">
          {(programme.outcomes || []).map((outcome, index) => (
            <div className="editable-block" key={`outcome-${index}`}>
              <div className="editable-row">
                <input value={outcome} onChange={(event) => updateOutcome(index, event.target.value)} />
                <button type="button" onClick={() => removeOutcome(index)} aria-label="Remove outcome">
                  x
                </button>
              </div>
              <SuggestionOptions
                label="Other outcome options"
                options={outcomeSuggestions(plan, index, outcome)}
                onSelect={(value) => updateOutcome(index, value)}
              />
            </div>
          ))}
        </div>
      </article>

      <div className="week-grid">
        {Object.entries(programme.weeklyStructure || {}).map(([week, topics]) => (
          <article className="week-card" key={week}>
            <div className="copy-card-header">
              <span>{week}</span>
              <button className="secondary-action" type="button" onClick={() => addWeekTopic(week)}>
                Add Topic
              </button>
            </div>
            <div className="programme-editor-list">
              {topics.map((topic, index) => (
                <div className="editable-block" key={`${week}-${index}`}>
                  <div className="editable-row">
                    <textarea value={topic} onChange={(event) => updateWeekTopic(week, index, event.target.value)} />
                    <button type="button" onClick={() => removeWeekTopic(week, index)} aria-label="Remove topic">
                      x
                    </button>
                  </div>
                  <SuggestionOptions
                    label="Other topic options"
                    options={topicSuggestions(plan, week, index, topic)}
                    onSelect={(value) => updateWeekTopic(week, index, value)}
                  />
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>

      <article className="assignment-panel">
        <span className="panel-label">Demo Pitch</span>
        <EditorTextarea value={programme.demoPitch || ""} onChange={(value) => patchProgramme({ demoPitch: value })} />
      </article>
    </div>
  );
}

function PersonalizedScreen({ plan, onRegenerate, onRegenerateQuestion, onChapterChange, onFinalAssignmentChange, loading }) {
  const [answers, setAnswers] = useState({});
  const chapters = plan.personalized.chapters;

  function updateChapterField(index, field, value) {
    onChapterChange(index, { ...chapters[index], [field]: value });
  }

  function updateGameField(index, field, value) {
    onChapterChange(index, {
      ...chapters[index],
      game: { ...chapters[index].game, [field]: value },
    });
  }

  return (
    <div className="content-stack">
      <ScreenHeader title="Personalized Learning" description={plan.personalized.studentProfile} />
      <ActionRow
        label={plan.personalized.usedFallback ? "Using offline fallback personalization" : `Generated by ${plan.provider?.name || "AI"}`}
        buttonLabel="Regenerate Personalized Learning"
        onClick={onRegenerate}
        disabled={Boolean(loading)}
      />

      <div className="chapter-grid">
        {chapters.map((chapter, index) => {
          const selected = answers[index];
          const isCorrect = selected === chapter.game.correctChoice;

          return (
            <article className="chapter-card" key={`${chapter.title}-${index}`}>
              <span className="chapter-number">Chapter {index + 1}</span>
              <EditorInput value={chapter.title} onChange={(value) => updateChapterField(index, "title", value)} />

              <div className="chapter-section">
                <span>Standard Explanation</span>
                <EditorTextarea value={chapter.standard} onChange={(value) => updateChapterField(index, "standard", value)} />
              </div>
              <div className="chapter-section personal">
                <span>Personalized for Nursing</span>
                <EditorTextarea value={chapter.personalized} onChange={(value) => updateChapterField(index, "personalized", value)} />
              </div>
              <div className="game-box">
                <div className="panel-label">
                  <Gamepad2 size={16} />
                  Mini-game
                </div>
                <EditorInput value={chapter.game.name} onChange={(value) => updateGameField(index, "name", value)} />
                <EditorTextarea value={chapter.game.description || ""} onChange={(value) => updateGameField(index, "description", value)} />
                <EditorTextarea value={chapter.game.scenario || ""} onChange={(value) => updateGameField(index, "scenario", value)} />
                <ChoicesEditor chapter={chapter} onChange={(choices) => updateGameField(index, "choices", choices)} />
                <label className="editor-label">
                  Correct answer
                  <select
                    value={chapter.game.correctChoice || chapter.game.choices?.[0] || ""}
                    onChange={(event) => updateGameField(index, "correctChoice", event.target.value)}
                  >
                    {(chapter.game.choices || []).map((choice) => (
                      <option key={choice} value={choice}>
                        {choice}
                      </option>
                    ))}
                  </select>
                </label>
                <EditorTextarea value={chapter.game.feedback || ""} onChange={(value) => updateGameField(index, "feedback", value)} />

                <button className="secondary-action full" type="button" disabled={Boolean(loading)} onClick={() => onRegenerateQuestion(index, chapter)}>
                  <RefreshCw size={15} />
                  Regenerate question again
                </button>

                <div className="play-card">
                  <strong>Play:</strong> {chapter.game.scenario}
                </div>
                <div className="choice-grid">
                  {(chapter.game.choices || []).map((choice) => (
                    <button
                      className={selected === choice ? "choice active" : "choice"}
                      key={choice}
                      type="button"
                      onClick={() => setAnswers((current) => ({ ...current, [index]: choice }))}
                    >
                      {choice}
                    </button>
                  ))}
                </div>
                {selected && (
                  <div className={isCorrect ? "feedback good" : "feedback"}>
                    {isCorrect ? chapter.game.feedback : `Try again. A stronger choice is: ${chapter.game.correctChoice}`}
                  </div>
                )}
              </div>
            </article>
          );
        })}
      </div>

      <article className="assignment-panel">
        <span className="panel-label">Final Assignment</span>
        <EditorTextarea value={plan.personalized.finalAssignment} onChange={onFinalAssignmentChange} />
      </article>
    </div>
  );
}

function TeacherScreen({ plan, emails, onSearchTalent, onGenerateEmail, loading }) {
  const [tab, setTab] = useState("available");
  const recommendedId = plan.teacher.teacher_id;

  return (
    <div className="content-stack">
      <ScreenHeader title="Teacher" description="Availability and likely external teaching candidates." />

      <div className="tabs" role="tablist" aria-label="Teacher views">
        <button className={tab === "available" ? "active" : ""} type="button" onClick={() => setTab("available")}>
          Available Teachers
        </button>
        <button className={tab === "recruitment" ? "active" : ""} type="button" onClick={() => setTab("recruitment")}>
          Recruitment Pool
        </button>
      </div>

      {tab === "available" && (
        <div className="teacher-grid">
          {plan.teachers.map((teacher) => (
            <article className={teacher.teacher_id === recommendedId ? "teacher-card recommended" : "teacher-card"} key={teacher.teacher_id}>
              <div className="teacher-card-head">
                <div>
                  <h3>{teacher.name}</h3>
                  <p>{teacher.teacher_id === recommendedId ? "Recommended teacher" : "Available teacher"}</p>
                </div>
                <strong>EUR {teacher.hourly_rate}/h</strong>
              </div>
              <ChipList items={teacher.skills} />
              <div className="teacher-meta">
                <span>{teacher.available_months.join(", ")}</span>
                <span>{teacher.available_modes.join(", ")}</span>
              </div>
            </article>
          ))}
        </div>
      )}

      {tab === "recruitment" && (
        <div className="talent-list">
          <ActionRow
            label={plan.talentStatus || "LinkedIn partner credentials are optional; local talent pool is ranked now."}
            buttonLabel="Search Talent Pool + LinkedIn"
            onClick={onSearchTalent}
            disabled={Boolean(loading)}
          />
          {plan.talent.map((candidate) => {
            const id = candidate.talent_id || candidate.name;
            const email = emails[id];
            return (
              <article className="talent-row" key={id}>
                <div className="talent-score">
                  <span>{candidate.matchScore}%</span>
                  <small>Match</small>
                </div>
                <div>
                  <h3>{candidate.name}</h3>
                  <p>
                    {candidate.headline} - {candidate.location}
                  </p>
                  <ChipList items={candidate.skills.slice(0, 7)} />
                  <p className="talent-note">{candidate.matchReasons.join("; ")}</p>
                  {email && (
                    <div className="email-draft">
                      <span>{email.usedFallback ? "Fallback recruitment email" : "AI-generated recruitment email"}</span>
                      <pre>{email.text}</pre>
                    </div>
                  )}
                </div>
                <div className="talent-actions">
                  <button className="secondary-action" type="button" disabled={Boolean(loading)} onClick={() => onGenerateEmail(candidate)}>
                    Email
                  </button>
                  <a href={candidate.linkedin_profile} target="_blank" rel="noreferrer" className="secondary-link">
                    Profile
                    <ChevronRight size={15} />
                  </a>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

function MarketingScreen({ plan, imagePaths, brochure, onRegenerateMarketing, onGenerateImage, onGenerateBrochure, loading }) {
  return (
    <div className="content-stack">
      <ScreenHeader title="Marketing" description={plan.marketing.tagline} />
      <ActionRow
        label={plan.marketing.usedFallback ? "Using offline fallback marketing content" : `Generated by ${plan.provider?.name || "AI"}`}
        buttonLabel="Regenerate Marketing Copy"
        onClick={onRegenerateMarketing}
        disabled={Boolean(loading)}
      />

      <div className="marketing-grid">
        <article className="copy-card wide">
          <span className="panel-label">Website Description</span>
          <p>{plan.marketing.website}</p>
        </article>
        <article className="copy-card">
          <span className="panel-label">Social Post</span>
          <p>{plan.marketing.social}</p>
        </article>
        <article className="copy-card">
          <span className="panel-label">Partner Email</span>
          <pre>{plan.marketing.email}</pre>
        </article>
      </div>

      <div className="asset-grid">
        <article className="asset-card">
          <img src={imagePaths.social || socialImage} alt="Generated social media visual for the short programme" />
          <div>
            <span className="panel-label">Social Visual</span>
            <p>Gemini image generation keeps the API key server-side.</p>
            <button className="secondary-action full" type="button" disabled={Boolean(loading)} onClick={() => onGenerateImage("social")}>
              Generate Social Image
            </button>
          </div>
        </article>
        <article className="asset-card">
          <img src={imagePaths.brochure || brochureImage} alt="Generated brochure cover for the short programme" />
          <div>
            <span className="panel-label">Brochure Cover</span>
            <p>Creates a branded visual asset in generated_assets.</p>
            <button className="secondary-action full" type="button" disabled={Boolean(loading)} onClick={() => onGenerateImage("brochure")}>
              Generate Brochure Image
            </button>
          </div>
        </article>
      </div>

      <article className="selling-panel">
        <h3>Selling Points</h3>
        <ul className="clean-list">
          {plan.marketing.sellingPoints.map((point) => (
            <li key={point}>
              <Check size={15} />
              {point}
            </li>
          ))}
        </ul>
      </article>

      <article className="copy-card">
        <div className="copy-card-header">
          <span className="panel-label">Brochure & Pamphlet Text</span>
          <button className="secondary-action" type="button" disabled={Boolean(loading)} onClick={onGenerateBrochure}>
            Generate Brochure
          </button>
        </div>
        {brochure ? <pre>{brochure}</pre> : <p>Generate a professional brochure or pamphlet for the programme using AI.</p>}
      </article>
    </div>
  );
}

function IncomeScreen({ plan }) {
  const [students, setStudents] = useState(25);
  const [price, setPrice] = useState(plan.market?.recommendedPrice || 450);
  const [costs, setCosts] = useState(4250);
  const result = computeFinance(students, price, costs);

  return (
    <div className="content-stack">
      <ScreenHeader title="Income" description="Revenue, profit, and break-even estimate." />

      <div className="control-grid">
        <RangeControl label="Expected Students" value={students} min={5} max={80} step={1} onChange={setStudents} />
        <RangeControl label="Price Per Student" value={price} min={150} max={1200} step={25} prefix="EUR " onChange={setPrice} />
        <RangeControl label="Estimated Costs" value={costs} min={1000} max={16000} step={250} prefix="EUR " onChange={setCosts} />
      </div>

      <div className="metric-grid">
        <MetricTile label="Revenue" value={`EUR ${result.revenue.toLocaleString()}`} />
        <MetricTile label="Profit" value={`EUR ${result.profit.toLocaleString()}`} tone={result.profit >= 0 ? "good" : "alert"} />
        <MetricTile label="Break-even Price" value={`EUR ${Math.round(result.breakEvenPrice).toLocaleString()}`} />
        <MetricTile label="Break-even Students" value={`~${result.breakEvenStudents}`} />
      </div>
    </div>
  );
}

function LockedScreen({ step }) {
  const Icon = stepIcons[step.id] || Lock;

  return (
    <div className="locked-screen">
      <div className="locked-icon">
        <Icon size={30} />
      </div>
      <h2>{step.label}</h2>
      <p>Generate the course plan from Trending Topics to unlock this section.</p>
    </div>
  );
}

function BrandMark({ compact = false }) {
  return (
    <span className={compact ? "brand-mark compact" : "brand-mark"} aria-hidden="true">
      <span className="tile yellow one" />
      <span className="tile yellow two" />
      <span className="tile black three" />
      <span className="tile black four" />
    </span>
  );
}

function IconButton({ label, icon: Icon }) {
  return (
    <button className="icon-button" type="button" aria-label={label} title={label}>
      <Icon size={18} />
    </button>
  );
}

function ScreenHeader({ title, description }) {
  return (
    <div className="screen-header">
      <h1 id="screen-title">{title}</h1>
      <p>{description}</p>
    </div>
  );
}

function ActionRow({ label, buttonLabel, onClick, disabled }) {
  return (
    <div className="action-row">
      <span>{label}</span>
      <button className="secondary-action" type="button" disabled={disabled} onClick={onClick}>
        <RefreshCw size={15} />
        {buttonLabel}
      </button>
    </div>
  );
}

function formatEUR(value) {
  const amount = Number(value || 0);
  return `EUR ${amount.toLocaleString()}`;
}

function StatusChip({ status }) {
  return <span className={`status-chip ${status.toLowerCase()}`}>{status}</span>;
}

function KeywordChip({ children, tone = "blue" }) {
  return <span className={`keyword-chip ${tone}`}>{children}</span>;
}

function ChipList({ items = [] }) {
  return (
    <div className="chip-row">
      {items.map((item, index) => (
        <KeywordChip key={item} tone={keywordTone[index % keywordTone.length]}>
          {item}
        </KeywordChip>
      ))}
    </div>
  );
}

function InfoPanel({ icon: Icon, label, title, children }) {
  return (
    <article className="info-panel">
      <div className="panel-label">
        <Icon size={16} />
        {label}
      </div>
      <h3>{title}</h3>
      {children}
    </article>
  );
}

function MetricTile({ label, value, tone = "", compact = false }) {
  return (
    <article className={`metric-tile ${tone} ${compact ? "compact" : ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function RangeControl({ label, value, min, max, step, prefix = "", onChange }) {
  return (
    <label className="range-control">
      <span>{label}</span>
      <strong>
        {prefix}
        {Number(value).toLocaleString()}
      </strong>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function EditorInput({ value, onChange }) {
  return <input className="editor-input" value={value || ""} onChange={(event) => onChange(event.target.value)} />;
}

function EditorTextarea({ value, onChange }) {
  return <textarea className="editor-textarea" value={value || ""} onChange={(event) => onChange(event.target.value)} />;
}

function ChoicesEditor({ chapter, onChange }) {
  return (
    <label className="editor-label">
      Answer choices
      <textarea
        className="editor-textarea compact"
        value={(chapter.game.choices || []).join("\n")}
        onChange={(event) => onChange(event.target.value.split("\n").map((item) => item.trim()).filter(Boolean))}
      />
    </label>
  );
}

export default App;
