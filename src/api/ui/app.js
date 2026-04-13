const elements = {
  pageTitle: document.querySelector("title"),
  heroStatus: document.getElementById("hero-status"),
  onboardingHeadline: document.getElementById("onboarding-headline"),
  onboardingSubtext: document.getElementById("onboarding-subtext"),
  onboardingWorkflow: document.getElementById("onboarding-workflow"),
  onboardingProgressLabel: document.getElementById("onboarding-progress-label"),
  onboardingProgressValue: document.getElementById("onboarding-progress-value"),
  onboardingProgressBar: document.getElementById("onboarding-progress-bar"),
  onboardingStepTitle: document.getElementById("onboarding-step-title"),
  onboardingStepSummary: document.getElementById("onboarding-step-summary"),
  onboardingStepWhy: document.getElementById("onboarding-step-why"),
  onboardingStepNext: document.getElementById("onboarding-step-next"),
  onboardingSafeNote: document.getElementById("onboarding-safe-note"),
  onboardingOpenLink: document.getElementById("onboarding-open-link"),
  onboardingMarkComplete: document.getElementById("onboarding-mark-complete"),
  onboardingNextStep: document.getElementById("onboarding-next-step"),
  onboardingReset: document.getElementById("onboarding-reset"),
  onboardingSteps: document.getElementById("onboarding-steps"),
  identitySummary: document.getElementById("identity-summary"),
  identitySubtext: document.getElementById("identity-subtext"),
  capabilityGrid: document.getElementById("capability-grid"),
  referenceHeadline: document.getElementById("reference-headline"),
  referenceSubtext: document.getElementById("reference-subtext"),
  referenceWorkflow: document.getElementById("reference-workflow"),
  referenceUserTask: document.getElementById("reference-user-task"),
  referenceProtection: document.getElementById("reference-protection"),
  referenceWhyItMatters: document.getElementById("reference-why-it-matters"),
  referenceFlowSelect: document.getElementById("reference-flow-select"),
  referenceFlowButton: document.getElementById("run-reference-flow"),
  referenceResultTitle: document.getElementById("reference-result-title"),
  referenceResultDecision: document.getElementById("reference-result-decision"),
  referenceResultMetrics: document.getElementById("reference-result-metrics"),
  referenceResultExplainer: document.getElementById("reference-result-explainer"),
  referenceResultJson: document.getElementById("reference-result-json"),
  shellHeadline: document.getElementById("shell-headline"),
  shellSubtext: document.getElementById("shell-subtext"),
  shellWhatIsHappening: document.getElementById("shell-what-is-happening"),
  shellWhyItMatters: document.getElementById("shell-why-it-matters"),
  shellNextStep: document.getElementById("shell-next-step"),
  summaryGrid: document.getElementById("summary-grid"),
  latestEvents: document.getElementById("latest-events"),
  historyFilter: document.getElementById("history-filter"),
  historyStatusFilter: document.getElementById("history-status-filter"),
  historyProviderFilter: document.getElementById("history-provider-filter"),
  refreshHistoryButton: document.getElementById("refresh-history"),
  shellHistoryHint: document.getElementById("shell-history-hint"),
  historyList: document.getElementById("history-list"),
  shellApprovalHint: document.getElementById("shell-approval-hint"),
  approvalQueueList: document.getElementById("approval-queue-list"),
  shellAuditHint: document.getElementById("shell-audit-hint"),
  auditDecisionFilter: document.getElementById("audit-decision-filter"),
  auditProviderFilter: document.getElementById("audit-provider-filter"),
  auditIntegrityFilter: document.getElementById("audit-integrity-filter"),
  refreshAuditButton: document.getElementById("refresh-audit"),
  auditList: document.getElementById("audit-list"),
  decisionGrid: document.getElementById("decision-grid"),
  scenarioSelect: document.getElementById("scenario-select"),
  runButton: document.getElementById("run-scenario"),
  resultTitle: document.getElementById("result-title"),
  resultDecision: document.getElementById("result-decision"),
  resultMetrics: document.getElementById("result-metrics"),
  resultExplainer: document.getElementById("result-explainer"),
  resultJson: document.getElementById("result-json"),
  integrationHeadline: document.getElementById("integration-headline"),
  integrationSubtext: document.getElementById("integration-subtext"),
  integrationConnectsTo: document.getElementById("integration-connects-to"),
  integrationWorkflow: document.getElementById("integration-workflow"),
  integrationDeveloperPlacement: document.getElementById("integration-developer-placement"),
  integrationHowToUse: document.getElementById("integration-how-to-use"),
  integrationGrid: document.getElementById("integration-grid"),
  integrationSelect: document.getElementById("integration-select"),
  integrationButton: document.getElementById("run-integration"),
  integrationAllowedList: document.getElementById("integration-allowed-list"),
  integrationBlockedList: document.getElementById("integration-blocked-list"),
  integrationResultTitle: document.getElementById("integration-result-title"),
  integrationResultDecision: document.getElementById("integration-result-decision"),
  integrationResultMetrics: document.getElementById("integration-result-metrics"),
  integrationResultExplainer: document.getElementById("integration-result-explainer"),
  integrationResultJson: document.getElementById("integration-result-json"),
  flowLine: document.getElementById("flow-line"),
  layerGrid: document.getElementById("layer-grid"),
  notIncludedList: document.getElementById("not-included-list"),
  usePathGrid: document.getElementById("use-path-grid"),
  audienceGrid: document.getElementById("audience-grid"),
  roadmapList: document.getElementById("roadmap-list"),
  providerHeadline: document.getElementById("providers-headline"),
  providerSubtext: document.getElementById("providers-subtext"),
  providerWhySafe: document.getElementById("providers-why-safe"),
  providersConfiguredHelp: document.getElementById("providers-configured-help"),
  providersEnabledHelp: document.getElementById("providers-enabled-help"),
  providersGuidanceList: document.getElementById("provider-guidance-list"),
  providerGrid: document.getElementById("provider-grid"),
  assistantHeadline: document.getElementById("assistant-headline"),
  assistantSubtext: document.getElementById("assistant-subtext"),
  assistantSafeNote: document.getElementById("assistant-safe-note"),
  assistantHowItWorks: document.getElementById("assistant-how-it-works"),
  assistantDataScope: document.getElementById("assistant-data-scope"),
  assistantResultTitle: document.getElementById("assistant-result-title"),
  assistantResultStatus: document.getElementById("assistant-result-status"),
  assistantStatusCopy: document.getElementById("assistant-status-copy"),
  assistantRunInsight: document.getElementById("assistant-run-insight"),
  assistantResultExplainer: document.getElementById("assistant-result-explainer"),
  assistantCapabilitiesGrid: document.getElementById("assistant-capabilities-grid"),
  assistantResultJson: document.getElementById("assistant-result-json"),
  languageSelect: document.getElementById("language-select"),
};

const decisionClassMap = {
  ALLOW: "allow",
  NEEDS_APPROVAL: "approval",
  DENY: "deny",
  WAITING: "",
};

const DEFAULT_LANG = "en";
const LANGUAGE_STORAGE_KEY = "safecore-ui-lang";
const ONBOARDING_STORAGE_KEY = "safecore-ui-onboarding";

let currentLang = loadStoredLang();
let currentLabels = null;
let cachedScenarios = [];
let cachedIntegrationExamples = [];
let cachedReferenceFlows = [];
let currentOnboarding = null;
let onboardingState = loadOnboardingState();
let assistantCapabilities = null;
let latestAssistantPayload = null;

function loadStoredLang() {
  try {
    return localStorage.getItem(LANGUAGE_STORAGE_KEY) || DEFAULT_LANG;
  } catch (error) {
    return DEFAULT_LANG;
  }
}

function storeLang(lang) {
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
  } catch (error) {
    // Ignore storage failures; the UI still works with in-memory state.
  }
}

function loadOnboardingState() {
  try {
    const raw = localStorage.getItem(ONBOARDING_STORAGE_KEY);
    if (!raw) {
      return { currentStepId: null, completed: [] };
    }
    const parsed = JSON.parse(raw);
    return {
      currentStepId: parsed.currentStepId || null,
      completed: Array.isArray(parsed.completed) ? parsed.completed : [],
    };
  } catch (error) {
    return { currentStepId: null, completed: [] };
  }
}

function storeOnboardingState() {
  try {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(onboardingState));
  } catch (error) {
    // Ignore storage failures; onboarding still works in memory.
  }
}

function buildUrl(path, params = {}) {
  const url = new URL(path, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });
  return `${url.pathname}${url.search}`;
}

async function fetchJson(path, params = {}) {
  const response = await fetch(buildUrl(path, params));
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function fetchJsonPost(path, body) {
  const response = await fetch(buildUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function getLabel(group, key, fallback = "") {
  return currentLabels?.[group]?.[key] || fallback;
}

function applyText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
}

function applyChromeLabels(labels) {
  currentLabels = labels;
  document.documentElement.lang = currentLang;
  if (elements.pageTitle) {
    elements.pageTitle.textContent = labels.page_title || "SafeCore Product Shell";
  }

  applyText("nav-overview", labels.navigation.overview);
  applyText("nav-onboarding", labels.navigation.onboarding);
  applyText("nav-product-shell", labels.navigation.product_shell);
  applyText("nav-providers", labels.navigation.providers);
  applyText("nav-assistant", labels.navigation.assistant);
  applyText("nav-history", labels.navigation.history);
  applyText("nav-approval-audit", labels.navigation.approval_audit);

  applyText("hero-eyebrow", labels.hero.eyebrow);
  applyText("hero-title", labels.hero.title);
  applyText("hero-lead", labels.hero.lead);
  applyText("hero-action-primary", labels.hero.action_primary);
  applyText("hero-action-secondary", labels.hero.action_secondary);
  applyText("language-label", labels.hero.language_label);

  applyText("overview-kicker", labels.sections.overview_kicker);
  applyText("overview-title", labels.sections.overview_title);
  applyText("project-identity-title", labels.sections.project_identity);
  applyText("what-safecore-does-title", labels.sections.what_safecore_does);
  applyText("onboarding-kicker", labels.sections.onboarding_kicker);
  applyText("onboarding-title", labels.sections.onboarding_title);
  applyText("onboarding-steps-title", labels.sections.onboarding_steps);
  applyText("reference-kicker", labels.sections.reference_kicker);
  applyText("reference-title", labels.sections.reference_title);
  applyText("reference-result-kicker", labels.sections.reference_result);
  applyText("product-shell-kicker", labels.sections.product_shell_kicker);
  applyText("product-shell-title", labels.sections.product_shell_title);
  applyText("operations-overview-title", labels.sections.operations_overview);
  applyText("latest-events-title", labels.sections.latest_events);
  applyText("providers-kicker", labels.sections.providers_kicker);
  applyText("providers-title", labels.sections.providers_title);
  applyText("providers-cards-title", labels.navigation.providers);
  applyText("assistant-kicker", labels.sections.assistant_kicker);
  applyText("assistant-title", labels.sections.assistant_title);
  applyText("assistant-result-kicker", labels.sections.assistant_result);
  applyText("history-kicker", labels.sections.history_kicker);
  applyText("history-title", labels.sections.history_title);
  applyText("recent-runs-title", labels.sections.recent_runs);
  applyText("approval-audit-kicker", labels.sections.approval_audit_kicker);
  applyText("approval-audit-title", labels.sections.approval_audit_title);
  applyText("approval-queue-title", labels.sections.approval_queue);
  applyText("audit-viewer-title", labels.sections.audit_viewer);
  applyText("decision-kicker", labels.sections.decision_kicker);
  applyText("decision-title", labels.sections.decision_title);
  applyText("demo-kicker", labels.sections.demo_kicker);
  applyText("demo-title", labels.sections.demo_title);
  applyText("scenario-result-kicker", labels.sections.scenario_result);
  applyText("integration-kicker", labels.sections.integration_kicker);
  applyText("integration-title", labels.sections.integration_title);
  applyText("integration-result-kicker", labels.sections.integration_result);
  applyText("architecture-kicker", labels.sections.architecture_kicker);
  applyText("architecture-title", labels.sections.architecture_title);
  applyText("scope-kicker", labels.sections.scope_kicker);
  applyText("scope-title", labels.sections.scope_title);
  applyText("use-today-title", labels.sections.use_today);
  applyText("boundaries-title", labels.sections.boundaries);
  applyText("audiences-kicker", labels.sections.audiences_kicker);
  applyText("audiences-title", labels.sections.audiences_title);
  applyText("roadmap-kicker", labels.sections.roadmap_kicker);
  applyText("roadmap-title", labels.sections.roadmap_title);

  applyText("reference-flow-label", labels.controls.choose_user_task);
  applyText("scenario-label", labels.controls.choose_demo_scenario);
  applyText("integration-label", labels.controls.choose_integration_example);
  applyText("history-filter-label", labels.controls.filter_by_decision);
  applyText("history-status-filter-label", labels.controls.filter_by_status);
  applyText("history-provider-filter-label", labels.controls.filter_by_provider);
  applyText("audit-decision-filter-label", labels.controls.filter_by_decision);
  applyText("audit-provider-filter-label", labels.controls.filter_by_provider);
  applyText("audit-integrity-filter-label", labels.controls.filter_by_integrity);

  elements.referenceFlowButton.textContent = labels.controls.run_reference_flow;
  elements.runButton.textContent = labels.controls.run_scenario;
  elements.integrationButton.textContent = labels.controls.run_integration;
  elements.assistantRunInsight.textContent = labels.controls.explain_latest_result;
  elements.refreshHistoryButton.textContent = labels.controls.refresh_history;
  elements.refreshAuditButton.textContent = labels.controls.refresh_audit;
  elements.onboardingMarkComplete.textContent = labels.controls.mark_complete;
  elements.onboardingNextStep.textContent = labels.controls.next_onboarding_step;
  elements.onboardingReset.textContent = labels.controls.reset_onboarding;

  applyText("reference-microcopy", labels.explanations.reference_microcopy);
  applyText("demo-microcopy", labels.explanations.demo_microcopy);
  applyText("integration-microcopy", labels.explanations.integration_microcopy);
  applyText("integration-allowed-title", labels.explanations.allowed_title);
  applyText("integration-blocked-title", labels.explanations.blocked_title);
  applyText("assistant-data-scope-title", labels.result_labels.data_scope);
  applyText("assistant-json-summary", labels.sections.assistant_result);
  applyText("providers-guidance-title", providerStatusTitle(labels));
}

function providerStatusTitle(labels) {
  return labels.sections.providers_title;
}

function renderLanguageOptions(languageState) {
  const supported = languageState?.supported || [];
  elements.languageSelect.innerHTML = "";
  supported.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.code;
    option.textContent = item.label;
    option.selected = item.code === languageState.selected;
    elements.languageSelect.appendChild(option);
  });
  elements.languageSelect.value = languageState?.selected || currentLang;
}

function normalizeOnboardingState(onboarding) {
  const steps = onboarding?.steps || [];
  const validIds = new Set(steps.map((step) => step.id));
  const completed = onboardingState.completed.filter((stepId) => validIds.has(stepId));
  const currentStepId =
    validIds.has(onboardingState.currentStepId)
      ? onboardingState.currentStepId
      : steps.find((step) => !completed.includes(step.id))?.id || steps[0]?.id || null;
  onboardingState = { currentStepId, completed };
  storeOnboardingState();
}

function markOnboardingStepComplete(stepId) {
  if (!stepId || onboardingState.completed.includes(stepId)) {
    return;
  }
  onboardingState.completed = [...onboardingState.completed, stepId];
  onboardingState.currentStepId = findNextOnboardingStep(stepId) || stepId;
  storeOnboardingState();
  renderOnboarding(currentOnboarding);
}

function selectOnboardingStep(stepId) {
  onboardingState.currentStepId = stepId;
  storeOnboardingState();
  renderOnboarding(currentOnboarding);
}

function resetOnboarding() {
  onboardingState = { currentStepId: currentOnboarding?.steps?.[0]?.id || null, completed: [] };
  storeOnboardingState();
  renderOnboarding(currentOnboarding);
}

function findNextOnboardingStep(stepId) {
  const steps = currentOnboarding?.steps || [];
  const currentIndex = steps.findIndex((step) => step.id === stepId);
  if (currentIndex < 0) {
    return steps[0]?.id || null;
  }
  const nextIncomplete = steps.slice(currentIndex + 1).find((step) => !onboardingState.completed.includes(step.id));
  if (nextIncomplete) {
    return nextIncomplete.id;
  }
  return steps[currentIndex + 1]?.id || steps[currentIndex]?.id || null;
}

function renderOnboarding(onboarding) {
  currentOnboarding = onboarding;
  normalizeOnboardingState(onboarding);
  const steps = onboarding?.steps || [];
  const currentStep =
    steps.find((step) => step.id === onboardingState.currentStepId) || steps[0] || null;
  const completedCount = onboardingState.completed.length;
  const progressPercent = steps.length ? Math.round((completedCount / steps.length) * 100) : 0;

  elements.onboardingHeadline.textContent = onboarding.headline;
  elements.onboardingSubtext.textContent = onboarding.subtext;
  elements.onboardingWorkflow.textContent = onboarding.workflow;
  elements.onboardingSafeNote.textContent = onboarding.safe_note;
  elements.onboardingProgressLabel.textContent = onboarding.status_labels.progress;
  elements.onboardingProgressValue.textContent = `${completedCount} / ${steps.length}`;
  elements.onboardingProgressBar.style.width = `${progressPercent}%`;

  if (currentStep) {
    elements.onboardingStepTitle.textContent = currentStep.title;
    elements.onboardingStepSummary.textContent = currentStep.summary;
    elements.onboardingStepWhy.textContent = `${getLabel("result_labels", "why_it_matters", "Why it matters")}: ${currentStep.why_it_matters}`;
    elements.onboardingStepNext.textContent = `${getLabel("result_labels", "next_step", "Next step")}: ${currentStep.what_to_do}`;
    elements.onboardingOpenLink.href = `#${currentStep.anchor}`;
    elements.onboardingOpenLink.textContent = currentStep.action_label || getLabel("controls", "open_section", "Open section");
  }

  elements.onboardingSteps.innerHTML = "";
  steps.forEach((step, index) => {
    const isCompleted = onboardingState.completed.includes(step.id);
    const isCurrent = step.id === onboardingState.currentStepId;
    const card = document.createElement("button");
    card.type = "button";
    card.className = `step-item${isCompleted ? " completed" : ""}${isCurrent ? " current" : ""}`;
    const statusLabel = isCompleted
      ? onboarding.status_labels.completed
      : isCurrent
        ? onboarding.status_labels.current
        : onboarding.status_labels.up_next;
    card.innerHTML = `
      <div class="step-item-head">
        <span class="step-index">${index + 1}</span>
        <div>
          <h4>${step.title}</h4>
          <p>${step.summary}</p>
        </div>
      </div>
      <span class="step-state">${statusLabel}</span>
    `;
    card.addEventListener("click", () => selectOnboardingStep(step.id));
    elements.onboardingSteps.appendChild(card);
  });
}

function renderSelectOptions(element, options, selectedValue) {
  element.innerHTML = "";
  options.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    option.selected = item.value === selectedValue;
    element.appendChild(option);
  });
}

function renderStatusChips(statuses) {
  elements.heroStatus.innerHTML = "";
  statuses.forEach((status, index) => {
    const chip = document.createElement("div");
    chip.className = "status-chip fade-up";
    chip.style.animationDelay = `${index * 80}ms`;
    chip.textContent = status;
    elements.heroStatus.appendChild(chip);
  });
}

function renderCapabilities(capabilities) {
  elements.capabilityGrid.innerHTML = "";
  capabilities.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "capability-card fade-up";
    card.style.animationDelay = `${index * 35}ms`;
    card.innerHTML = `<h4>${item.title}</h4><p>${item.detail}</p>`;
    elements.capabilityGrid.appendChild(card);
  });
}

function renderProductShellContent(shellContent) {
  const labels = currentLabels.result_labels;
  elements.shellHeadline.textContent = shellContent.headline;
  elements.shellSubtext.textContent = shellContent.subtext;
  elements.shellWhatIsHappening.textContent = `${labels.meaning}: ${shellContent.what_is_happening}`;
  elements.shellWhyItMatters.textContent = `${labels.why_it_matters}: ${shellContent.why_it_matters}`;
  elements.shellNextStep.textContent = `${labels.next_step}: ${shellContent.what_to_do_next}`;
  elements.shellHistoryHint.textContent = shellContent.history_hint;
  elements.shellApprovalHint.textContent = shellContent.approval_hint;
  elements.shellAuditHint.textContent = shellContent.audit_hint;
}

function renderReferenceProductOverview(referenceProduct) {
  const labels = currentLabels.result_labels;
  elements.referenceHeadline.textContent = referenceProduct.headline;
  elements.referenceSubtext.textContent = referenceProduct.subtext;
  elements.referenceWorkflow.textContent = referenceProduct.workflow;
  elements.referenceUserTask.textContent = `${labels.user_task}: ${referenceProduct.what_user_is_doing}`;
  elements.referenceProtection.textContent = `${labels.what_protects}: ${referenceProduct.what_safecore_is_protecting}`;
  elements.referenceWhyItMatters.textContent = `${labels.why_it_matters}: ${referenceProduct.why_it_matters}`;
}

function renderReferenceFlowOptions(flows) {
  elements.referenceFlowSelect.innerHTML = "";
  flows.forEach((flow) => {
    const option = document.createElement("option");
    option.value = flow.name;
    option.textContent = `${flow.name} - ${flow.title}`;
    elements.referenceFlowSelect.appendChild(option);
  });
}

function renderDecisionCards(scenarios) {
  const labels = currentLabels.result_labels;
  elements.decisionGrid.innerHTML = "";
  scenarios.forEach((item, index) => {
    const slug = decisionClassMap[item.title] || "";
    const card = document.createElement("article");
    card.className = `decision-card ${slug} fade-up`;
    card.style.animationDelay = `${index * 45}ms`;
    card.innerHTML = `
      <span class="decision-badge ${slug}">${item.title}</span>
      <h3>${item.meaning}</h3>
      <p><strong>${labels.example}:</strong> ${item.example}</p>
      <p><strong>${labels.why_it_matters}:</strong> ${item.why_it_matters}</p>
      <p><strong>${labels.current_behavior}:</strong> ${item.current_rc_behavior}</p>
    `;
    elements.decisionGrid.appendChild(card);
  });
}

function renderArchitecture(architecture) {
  elements.flowLine.textContent = architecture.flow;
  elements.layerGrid.innerHTML = "";
  architecture.layers.forEach((layer, index) => {
    const card = document.createElement("article");
    card.className = "layer-card fade-up";
    card.style.animationDelay = `${index * 35}ms`;
    card.innerHTML = `<h3>${layer.title}</h3><p>${layer.detail}</p>`;
    elements.layerGrid.appendChild(card);
  });
}

function renderScope(scope) {
  elements.usePathGrid.innerHTML = "";
  scope.current_use.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "use-card fade-up";
    card.style.animationDelay = `${index * 40}ms`;
    card.innerHTML = `<h3>${item.title}</h3><p>${item.detail}</p>`;
    elements.usePathGrid.appendChild(card);
  });

  elements.notIncludedList.innerHTML = "";
  scope.not_included.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    elements.notIncludedList.appendChild(li);
  });
}

function renderAudiences(audiences) {
  elements.audienceGrid.innerHTML = "";
  audiences.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "audience-card fade-up";
    card.style.animationDelay = `${index * 40}ms`;
    card.innerHTML = `<h3>${item.title}</h3><p>${item.detail}</p>`;
    elements.audienceGrid.appendChild(card);
  });
}

function renderRoadmap(items) {
  elements.roadmapList.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    elements.roadmapList.appendChild(li);
  });
}

function renderProductShellSummary(summary) {
  const cards = [
    [getLabel("sections", "recent_runs", "Runs"), summary.total_runs],
    ["ALLOW", summary.allow],
    ["NEEDS_APPROVAL", summary.needs_approval],
    ["DENY", summary.deny],
    [getLabel("result_labels", "blocked", "Blocked"), summary.blocked],
    [getLabel("result_labels", "audit_integrity", "Audit integrity"), summary.audit_integrity_issues],
  ];
  elements.summaryGrid.innerHTML = "";
  cards.forEach(([label, value], index) => {
    const card = document.createElement("article");
    card.className = "metric-card fade-up";
    card.style.animationDelay = `${index * 25}ms`;
    card.innerHTML = `
      <span class="metric-label">${label}</span>
      <span class="metric-value">${value}</span>
    `;
    elements.summaryGrid.appendChild(card);
  });

  elements.latestEvents.innerHTML = "";
  if (!summary.latest_events.length) {
    elements.latestEvents.innerHTML = `<p class="empty-state">${currentLabels.empty_states.summary}</p>`;
    return;
  }
  summary.latest_events.forEach((event) => {
    const item = document.createElement("article");
    item.className = "timeline-item";
    item.innerHTML = `
      <p class="timeline-meta">${event.recorded_at || ""} - ${event.source || "run"}</p>
      <h4>${event.title || getLabel("result_labels", "run", "Run")}</h4>
      <p>${event.summary || ""}</p>
      <p class="microcopy">${getLabel("result_labels", "decision", "Decision")}: ${event.decision} - ${getLabel("result_labels", "blocked", "Blocked")}: ${String(event.blocked)}</p>
      <p class="microcopy">${getLabel("result_labels", "provider", "Provider mode")}: ${event.provider_mode_label || event.provider_mode || "LOCAL_DEMO"} - ${getLabel("result_labels", "run_status", "Run status")}: ${event.run_status_label || event.run_status || "N/A"}</p>
    `;
    elements.latestEvents.appendChild(item);
  });
}

function renderRunHistory(runs) {
  const labels = currentLabels.result_labels;
  elements.historyList.innerHTML = "";
  if (!runs.length) {
    elements.historyList.innerHTML = `<p class="empty-state">${currentLabels.empty_states.history}</p>`;
    return;
  }
  runs.forEach((run) => {
    const item = document.createElement("article");
    item.className = "history-item";
    item.innerHTML = `
      <div class="history-head">
        <div>
          <p class="timeline-meta">${run.recorded_at || ""} - ${run.source || "run"}</p>
          <h4>${run.title || run.name || labels.run}</h4>
        </div>
        <span class="decision-badge ${decisionClassMap[String(run.decision || "").toUpperCase()] || ""}">${run.decision || "WAITING"}</span>
      </div>
      <div class="history-metrics">
        <span>${labels.risk_score} ${run.risk_score}</span>
        <span>${labels.blocked} ${String(run.blocked)}</span>
        <span>${labels.approval} ${run.approval_status || "N/A"}</span>
        <span>${labels.audit_integrity} ${String(run.audit_integrity)}</span>
      </div>
      <p class="microcopy">${labels.run_status}: ${run.run_status_label || run.run_status || "N/A"} - ${labels.provider}: ${run.provider_mode_label || run.provider_mode || "LOCAL_DEMO"}</p>
      <p>${run.short_explanation || ""}</p>
      <p class="microcopy">${labels.what_next}: ${run.next_step || ""}</p>
    `;
    elements.historyList.appendChild(item);
  });
}

function renderApprovalQueue(items) {
  const labels = currentLabels.result_labels;
  elements.approvalQueueList.innerHTML = "";
  if (!items.length) {
    elements.approvalQueueList.innerHTML = `<p class="empty-state">${currentLabels.empty_states.queue}</p>`;
    return;
  }
  items.forEach((item) => {
    const checks = (item.operator_checks || []).map((check) => `<li>${check}</li>`).join("");
    const card = document.createElement("article");
    card.className = "queue-item";
    card.innerHTML = `
      <p class="timeline-meta">${item.recorded_at || ""} - ${item.source || "run"}</p>
      <h4>${item.title || getLabel("sections", "approval_queue", "Approval item")}</h4>
      <p><strong>${labels.why_waiting}:</strong> ${item.why_blocked || ""}</p>
      <p><strong>${labels.what_to_check}:</strong></p>
      <ul class="limit-list compact">${checks || `<li>${item.next_step || ""}</li>`}</ul>
      <p class="microcopy">${labels.status}: ${item.approval_status} - ${labels.escalation}: ${item.escalation_state} - ${labels.next_step}: ${item.next_step || ""}</p>
    `;
    elements.approvalQueueList.appendChild(card);
  });
}

function renderAuditView(records) {
  const labels = currentLabels.result_labels;
  elements.auditList.innerHTML = "";
  if (!records.length) {
    elements.auditList.innerHTML = `<p class="empty-state">${currentLabels.empty_states.audit}</p>`;
    return;
  }
  records.forEach((record) => {
    const card = document.createElement("article");
    card.className = "audit-item";
    card.innerHTML = `
      <p class="timeline-meta">${record.timestamp || ""} - ${record.step || "audit"}</p>
      <h4>${record.action || "audit_event"}</h4>
      <p>${labels.run}: ${record.run_id || "unknown"} - ${labels.decision}: ${record.decision || "N/A"}</p>
      <p>${record.plain_summary || ""}</p>
      <p class="microcopy">${labels.integrity}: ${record.integrity_state_label || record.integrity_state} - ${labels.provider}: ${record.provider_mode_label || record.provider_mode || "LOCAL_DEMO"}</p>
      <p class="microcopy">${labels.run_status}: ${record.run_status_label || record.run_status || "N/A"} - ${labels.audit_file}: ${record.audit_path}</p>
      <p class="microcopy">${labels.next_step}: ${record.next_step || ""}</p>
    `;
    elements.auditList.appendChild(card);
  });
}

function renderScenarioOptions(scenarios) {
  elements.scenarioSelect.innerHTML = "";
  scenarios.forEach((scenario) => {
    const option = document.createElement("option");
    option.value = scenario.name;
    option.textContent = `${scenario.name} - ${scenario.title}`;
    elements.scenarioSelect.appendChild(option);
  });
}

function renderIntegrationOverview(safeIntegration) {
  const labels = currentLabels.result_labels;
  elements.integrationHeadline.textContent = safeIntegration.headline;
  elements.integrationSubtext.textContent = safeIntegration.subtext;
  elements.integrationConnectsTo.textContent = safeIntegration.connects_to;
  elements.integrationWorkflow.textContent = safeIntegration.workflow;
  elements.integrationDeveloperPlacement.textContent = `${labels.what_protects}: ${safeIntegration.developer_placement}`;
  elements.integrationHowToUse.textContent = `${labels.next_step}: ${safeIntegration.how_to_use}`;

  elements.integrationGrid.innerHTML = "";
  safeIntegration.examples.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "use-card fade-up";
    card.style.animationDelay = `${index * 35}ms`;
    card.innerHTML = `<h3>${item.title}</h3><p>${item.meaning}</p><p><strong>${labels.example}:</strong> ${item.example}</p>`;
    elements.integrationGrid.appendChild(card);
  });

  elements.integrationAllowedList.innerHTML = "";
  safeIntegration.allowed.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    elements.integrationAllowedList.appendChild(li);
  });

  elements.integrationBlockedList.innerHTML = "";
  safeIntegration.blocked.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    elements.integrationBlockedList.appendChild(li);
  });
}

function renderIntegrationOptions(examples) {
  elements.integrationSelect.innerHTML = "";
  examples.forEach((example) => {
    const option = document.createElement("option");
    option.value = example.name;
    option.textContent = `${example.name} - ${example.title}`;
    elements.integrationSelect.appendChild(option);
  });
}

function renderProviderStatus(providerStatus) {
  const fieldLabels = providerStatus.field_labels || {
    configured: "Configured",
    enabled: "Enabled",
    key: "Key",
    source: "Source",
    base_url: "Base URL",
    gateway: "Gateway",
    health: "Health",
    capabilities: "Capabilities",
    next_step: "How to enable",
  };
  elements.providerHeadline.textContent = providerStatus.headline;
  elements.providerSubtext.textContent = providerStatus.subtext;
  elements.providerWhySafe.textContent = providerStatus.why_safe;
  elements.providersConfiguredHelp.textContent = providerStatus.configured_help || "";
  elements.providersEnabledHelp.textContent = [providerStatus.enabled_help, providerStatus.gateway_help]
    .filter(Boolean)
    .join(" ");
  applyText("providers-guidance-title", providerStatus.how_to_enable_title || getLabel("controls", "open_section", "How to enable"));
  elements.providersGuidanceList.innerHTML = "";
  (providerStatus.how_to_enable_steps || []).forEach((step) => {
    const li = document.createElement("li");
    li.textContent = step;
    elements.providersGuidanceList.appendChild(li);
  });
  elements.providerGrid.innerHTML = "";

  providerStatus.providers.forEach((provider, index) => {
    const card = document.createElement("article");
    const stateClass = provider.enabled ? "enabled" : provider.configured ? "configured" : "inactive";
    const capabilities = provider.capabilities || [];
    const capabilitiesText = capabilities.map((item) => item.name).join(", ");
    const healthSummary = provider.health?.summary || "";
    card.className = `provider-card fade-up ${stateClass}`;
    card.style.animationDelay = `${index * 35}ms`;
    card.innerHTML = `
      <div class="provider-card-head">
        <div>
          <p class="timeline-meta">${provider.mode}</p>
          <h4>${provider.name}</h4>
        </div>
        <span class="provider-pill ${stateClass}">${provider.enabled_label}</span>
      </div>
      <p>${provider.purpose}</p>
      <div class="provider-meta">
        <div class="provider-meta-row">
          <span class="metric-label">${fieldLabels.configured}</span>
          <span class="provider-meta-value">${provider.configured_label}</span>
        </div>
        <div class="provider-meta-row">
          <span class="metric-label">${fieldLabels.enabled}</span>
          <span class="provider-meta-value">${provider.enabled_label}</span>
        </div>
        <div class="provider-meta-row">
          <span class="metric-label">${fieldLabels.key}</span>
          <span class="provider-meta-value">${provider.key_status}</span>
        </div>
        <div class="provider-meta-row">
          <span class="metric-label">${fieldLabels.source}</span>
          <span class="provider-meta-value">${provider.env_source}</span>
        </div>
        <div class="provider-meta-row">
          <span class="metric-label">${fieldLabels.base_url}</span>
          <span class="provider-meta-value">${provider.base_url_label || "Not configured"}</span>
        </div>
        <div class="provider-meta-row">
          <span class="metric-label">${fieldLabels.gateway}</span>
          <span class="provider-meta-value">${provider.gateway_support || "Baseline"}</span>
        </div>
        <div class="provider-meta-row">
          <span class="metric-label">${fieldLabels.health}</span>
          <span class="provider-meta-value">${healthSummary}</span>
        </div>
      </div>
      ${capabilitiesText ? `<p class="microcopy"><strong>${fieldLabels.capabilities}:</strong> ${capabilitiesText}</p>` : ""}
      <p class="microcopy">${provider.status_summary || ""}</p>
      <p class="microcopy"><strong>${fieldLabels.next_step}:</strong> ${provider.how_to_enable || ""}</p>
      <p class="microcopy">${provider.safe_note}</p>
    `;
    elements.providerGrid.appendChild(card);
  });
}

function setStaticBadge(element, value) {
  element.className = "decision-badge";
  element.textContent = String(value || "WAITING").toUpperCase();
}

function renderAssistantPanel(content, capabilities) {
  assistantCapabilities = capabilities;
  const labels = currentLabels.result_labels;
  elements.assistantHeadline.textContent = capabilities.headline || content.headline;
  elements.assistantSubtext.textContent = [content.subtext, capabilities.subtext].filter(Boolean).join(" ");
  elements.assistantSafeNote.textContent = capabilities.safe_note || "";
  elements.assistantHowItWorks.textContent = `${labels.meaning}: ${content.how_it_works} ${labels.why_it_matters}: ${content.why_it_matters}`;
  elements.assistantDataScope.innerHTML = "";
  (capabilities.data_scope || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    elements.assistantDataScope.appendChild(li);
  });
  renderMetrics(elements.assistantCapabilitiesGrid, [
    [labels.status, capabilities.status_label],
    [labels.advisory_mode, capabilities.mode],
    [labels.provider, capabilities.provider],
    ["Base URL", capabilities.base_url],
  ]);
  if (latestAssistantPayload && capabilities.enabled) {
    requestAssistantInsight().catch((error) => renderAssistantError(error));
    return;
  }
  renderAssistantIdleState();
}

function renderAssistantIdleState() {
  const enabled = assistantCapabilities?.enabled;
  elements.assistantResultTitle.textContent = enabled ? "Run a guarded flow" : "Assistant disabled by default";
  setStaticBadge(elements.assistantResultStatus, enabled ? "WAITING" : "DISABLED");
  elements.assistantStatusCopy.textContent = assistantCapabilities?.availability_reason || currentLabels.empty_states.assistant;
  elements.assistantResultExplainer.innerHTML = `<p class="empty-state">${latestAssistantPayload ? currentLabels.empty_states.assistant : currentLabels.empty_states.assistant}</p>`;
  elements.assistantResultJson.textContent = "";
  elements.assistantRunInsight.disabled = !enabled || !latestAssistantPayload;
}

function renderAssistantInsight(payload) {
  const labels = currentLabels.result_labels;
  const insight = payload.insight;
  if (!payload.enabled || !insight) {
    renderAssistantIdleState();
    return;
  }
  elements.assistantRunInsight.disabled = false;
  elements.assistantResultTitle.textContent = payload.context?.user_intent || "Latest guarded result";
  setDecisionBadge(elements.assistantResultStatus, payload.decision);
  elements.assistantStatusCopy.textContent = assistantCapabilities?.availability_reason || "";
  elements.assistantResultExplainer.innerHTML = `
    <p><strong>${labels.assistant_summary}:</strong> ${insight.summary}</p>
    <p><strong>${labels.highlighted_risks}:</strong> ${(insight.highlighted_risks || []).join("; ") || "N/A"}</p>
    <p><strong>${labels.operator_guidance}:</strong> ${(insight.operator_guidance || []).join("; ") || "N/A"}</p>
    <p><strong>${labels.suggested_follow_up}:</strong> ${(insight.suggested_follow_up || []).join("; ") || "N/A"}</p>
    <p><strong>${labels.what_next}:</strong> ${insight.policy_suggestion_summary || ""}</p>
  `;
  elements.assistantResultJson.textContent = JSON.stringify(payload, null, 2);
}

function renderAssistantError(error) {
  elements.assistantResultTitle.textContent = getLabel("errors", "assistant_failed", "Assistant insight failed");
  setStaticBadge(elements.assistantResultStatus, "WAITING");
  elements.assistantStatusCopy.textContent = error.message;
  elements.assistantResultExplainer.innerHTML = `<p class="empty-state">${error.message}</p>`;
  elements.assistantResultJson.textContent = "";
  elements.assistantRunInsight.disabled = false;
}

async function requestAssistantInsight() {
  if (!latestAssistantPayload) {
    renderAssistantIdleState();
    return;
  }
  elements.assistantRunInsight.disabled = true;
  elements.assistantRunInsight.textContent = getLabel("controls", "running", "Running...");
  try {
    const payload = await fetchJsonPost("/v1/demo-ui/assistant-insight", {
      lang: currentLang,
      source: latestAssistantPayload.source,
      payload: latestAssistantPayload.payload,
    });
    renderAssistantInsight(payload);
  } catch (error) {
    renderAssistantError(error);
  } finally {
    elements.assistantRunInsight.textContent = getLabel("controls", "explain_latest_result", "Explain latest result");
    elements.assistantRunInsight.disabled = !assistantCapabilities?.enabled || !latestAssistantPayload;
  }
}

function setLatestAssistantPayload(source, payload) {
  latestAssistantPayload = { source, payload };
  if (assistantCapabilities?.enabled) {
    requestAssistantInsight().catch((error) => renderAssistantError(error));
  } else {
    renderAssistantIdleState();
  }
}

function renderHistoryFilters(filterState) {
  renderSelectOptions(
    elements.historyFilter,
    filterState.decision || [],
    elements.historyFilter.value || "ALL",
  );
  renderSelectOptions(
    elements.historyStatusFilter,
    filterState.run_status || [],
    elements.historyStatusFilter.value || "ALL",
  );
  renderSelectOptions(
    elements.historyProviderFilter,
    filterState.provider || [],
    elements.historyProviderFilter.value || "ALL",
  );
}

function renderAuditFilters(filterState) {
  renderSelectOptions(
    elements.auditDecisionFilter,
    filterState.decision || [],
    elements.auditDecisionFilter.value || "ALL",
  );
  renderSelectOptions(
    elements.auditProviderFilter,
    filterState.provider || [],
    elements.auditProviderFilter.value || "ALL",
  );
  renderSelectOptions(
    elements.auditIntegrityFilter,
    filterState.integrity || [],
    elements.auditIntegrityFilter.value || "ALL",
  );
}

function setDecisionBadge(element, decision) {
  const normalized = String(decision || "WAITING").toUpperCase();
  const decisionClass = decisionClassMap[normalized] || "";
  element.className = `decision-badge ${decisionClass}`;
  element.textContent = normalized;
}

function renderMetrics(target, metrics) {
  target.innerHTML = "";
  metrics.forEach(([label, value], index) => {
    const card = document.createElement("article");
    card.className = "metric-card fade-up";
    card.style.animationDelay = `${index * 25}ms`;
    card.innerHTML = `
      <span class="metric-label">${label}</span>
      <span class="metric-value">${value}</span>
    `;
    target.appendChild(card);
  });
}

function renderScenarioResult(payload) {
  const summary = payload.summary;
  const labels = currentLabels.result_labels;
  elements.resultTitle.textContent = payload.scenario;
  setDecisionBadge(elements.resultDecision, summary.decision);
  renderMetrics(elements.resultMetrics, [
    [labels.decision, summary.decision],
    [labels.risk_score, summary.risk_score],
    [labels.blocked, String(summary.blocked)],
    [labels.approval, summary.approval_status],
    [labels.execution, summary.execution_status],
    [labels.audit_integrity, String(summary.audit_integrity)],
  ]);
  elements.resultExplainer.innerHTML = `
    <p><strong>${labels.meaning}:</strong> ${payload.meaning}</p>
    <p><strong>${labels.example}:</strong> ${payload.example}</p>
    <p><strong>${labels.why_it_matters}:</strong> ${payload.why_it_matters}</p>
    <p><strong>${labels.current_behavior}:</strong> ${payload.current_rc_behavior}</p>
    <p><strong>${labels.audit_path}:</strong> ${summary.audit_path}</p>
  `;
  elements.resultJson.textContent = JSON.stringify(payload.result, null, 2);
}

function renderIntegrationResult(payload) {
  const summary = payload.summary;
  const labels = currentLabels.result_labels;
  elements.integrationResultTitle.textContent = payload.example;
  setDecisionBadge(elements.integrationResultDecision, summary.decision);
  renderMetrics(elements.integrationResultMetrics, [
    [labels.decision, summary.decision],
    [labels.risk_score, summary.risk_score],
    [labels.blocked, String(summary.blocked)],
    [labels.approval, summary.approval_status],
    [labels.connector, summary.connector_status],
    [labels.execution, summary.execution_status],
    [labels.audit_integrity, String(summary.audit_integrity)],
  ]);
  elements.integrationResultExplainer.innerHTML = `
    <p><strong>${labels.meaning}:</strong> ${payload.meaning}</p>
    <p><strong>${labels.example}:</strong> ${payload.example_text}</p>
    <p><strong>${labels.why_it_matters}:</strong> ${payload.why_it_matters}</p>
    <p><strong>${labels.current_behavior}:</strong> ${payload.current_rc_behavior}</p>
    <p><strong>${labels.audit_path}:</strong> ${summary.audit_path}</p>
  `;
  elements.integrationResultJson.textContent = JSON.stringify(payload.result, null, 2);
}

function renderReferenceProductResult(payload) {
  const summary = payload.summary;
  const labels = currentLabels.result_labels;
  elements.referenceResultTitle.textContent = payload.title;
  setDecisionBadge(elements.referenceResultDecision, summary.decision);
  renderMetrics(elements.referenceResultMetrics, [
    [labels.decision, summary.decision],
    [labels.risk_score, summary.risk_score],
    [labels.blocked, String(summary.blocked)],
    [labels.approval, summary.approval_status],
    [labels.connector, summary.connector_status],
    [labels.execution, summary.execution_status],
    [labels.audit_integrity, String(summary.audit_integrity)],
  ]);
  elements.referenceResultExplainer.innerHTML = `
    <p><strong>${labels.user_task}:</strong> ${payload.user_task}</p>
    <p><strong>${labels.what_protects}:</strong> ${payload.what_safecore_protects}</p>
    <p><strong>${labels.why_it_matters}:</strong> ${payload.why_it_matters}</p>
    <p><strong>${labels.short_explanation}:</strong> ${payload.short_explanation}</p>
    <p><strong>${labels.audit_path}:</strong> ${summary.audit_path}</p>
  `;
  elements.referenceResultJson.textContent = JSON.stringify(payload.result, null, 2);
}

async function runScenario(name) {
  elements.runButton.disabled = true;
  elements.runButton.textContent = getLabel("controls", "running", "Running...");
  try {
    const payload = await fetchJson(`/v1/demo-ui/scenarios/${name}`, { lang: currentLang });
    renderScenarioResult(payload);
    setLatestAssistantPayload("demo_scenario", payload);
    if (payload.summary?.approval_status === "PENDING") {
      markOnboardingStepComplete("approval_explanation");
    }
    await refreshProductShell();
  } catch (error) {
    elements.resultTitle.textContent = getLabel("errors", "scenario_failed", "Scenario failed");
    setDecisionBadge(elements.resultDecision, "WAITING");
    elements.resultMetrics.innerHTML = "";
    elements.resultExplainer.innerHTML = `<p><strong>Error:</strong> ${error.message}</p>`;
    elements.resultJson.textContent = "";
  } finally {
    elements.runButton.disabled = false;
    elements.runButton.textContent = getLabel("controls", "run_scenario", "Run scenario");
  }
}

async function runIntegrationExample(name) {
  elements.integrationButton.disabled = true;
  elements.integrationButton.textContent = getLabel("controls", "running", "Running...");
  try {
    const payload = await fetchJson(`/v1/demo-ui/integration-examples/${name}`, { lang: currentLang });
    renderIntegrationResult(payload);
    setLatestAssistantPayload("safe_integration", payload);
    if (payload.summary?.decision === "ALLOW" && payload.summary?.blocked === false) {
      markOnboardingStepComplete("first_safe_run");
    }
    await refreshProductShell();
  } catch (error) {
    elements.integrationResultTitle.textContent = getLabel("errors", "integration_failed", "Integration example failed");
    setDecisionBadge(elements.integrationResultDecision, "WAITING");
    elements.integrationResultMetrics.innerHTML = "";
    elements.integrationResultExplainer.innerHTML = `<p><strong>Error:</strong> ${error.message}</p>`;
    elements.integrationResultJson.textContent = "";
  } finally {
    elements.integrationButton.disabled = false;
    elements.integrationButton.textContent = getLabel("controls", "run_integration", "Run integration example");
  }
}

async function runReferenceProductFlow(name) {
  elements.referenceFlowButton.disabled = true;
  elements.referenceFlowButton.textContent = getLabel("controls", "running", "Running...");
  try {
    const payload = await fetchJson(`/v1/demo-ui/reference-product-flows/${name}`, { lang: currentLang });
    renderReferenceProductResult(payload);
    setLatestAssistantPayload("reference_product", payload);
    if (payload.summary?.decision === "ALLOW" && payload.summary?.blocked === false) {
      markOnboardingStepComplete("first_safe_run");
    }
    await refreshProductShell();
  } catch (error) {
    elements.referenceResultTitle.textContent = getLabel("errors", "reference_failed", "Reference product flow failed");
    setDecisionBadge(elements.referenceResultDecision, "WAITING");
    elements.referenceResultMetrics.innerHTML = "";
    elements.referenceResultExplainer.innerHTML = `<p><strong>Error:</strong> ${error.message}</p>`;
    elements.referenceResultJson.textContent = "";
  } finally {
    elements.referenceFlowButton.disabled = false;
    elements.referenceFlowButton.textContent = getLabel("controls", "run_reference_flow", "Run reference flow");
  }
}

async function refreshProductShell() {
  const overview = await fetchJson("/v1/demo-ui/product-shell", { lang: currentLang });
  renderHistoryFilters(overview.history_filters || {});
  renderAuditFilters(overview.audit_filters || {});
  renderProductShellSummary(overview.summary);
  renderRunHistory(overview.history);
  renderApprovalQueue(overview.approval_queue);
  renderAuditView(overview.audit_view);
  if ((overview.audit_view || []).length) {
    markOnboardingStepComplete("audit_viewer");
  }
}

async function refreshRunHistory() {
  elements.refreshHistoryButton.disabled = true;
  elements.refreshHistoryButton.textContent = getLabel("controls", "refreshing", "Refreshing...");
  try {
    const decision = elements.historyFilter.value;
    const runStatus = elements.historyStatusFilter.value;
    const provider = elements.historyProviderFilter.value;
    const payload = await fetchJson("/v1/demo-ui/product-shell/history", {
      decision,
      run_status: runStatus,
      provider,
      lang: currentLang,
    });
    renderHistoryFilters(payload.filters || {});
    elements.historyFilter.value = payload.decision_filter || decision;
    elements.historyStatusFilter.value = payload.run_status_filter || runStatus;
    elements.historyProviderFilter.value = payload.provider_filter || provider;
    renderRunHistory(payload.runs);
  } catch (error) {
    elements.historyList.innerHTML = `<p class="empty-state">${getLabel("errors", "history_failed", "History failed to load")}: ${error.message}</p>`;
  } finally {
    elements.refreshHistoryButton.disabled = false;
    elements.refreshHistoryButton.textContent = getLabel("controls", "refresh_history", "Refresh history");
  }
}

async function refreshAuditView() {
  elements.refreshAuditButton.disabled = true;
  elements.refreshAuditButton.textContent = getLabel("controls", "refreshing", "Refreshing...");
  try {
    const decision = elements.auditDecisionFilter.value;
    const provider = elements.auditProviderFilter.value;
    const integrityState = elements.auditIntegrityFilter.value;
    const payload = await fetchJson("/v1/demo-ui/product-shell/audit-view", {
      decision,
      provider,
      integrity_state: integrityState,
      lang: currentLang,
    });
    renderAuditFilters(payload.filters || {});
    elements.auditDecisionFilter.value = payload.decision_filter || decision;
    elements.auditProviderFilter.value = payload.provider_filter || provider;
    elements.auditIntegrityFilter.value = payload.integrity_filter || integrityState;
    renderAuditView(payload.records);
    if ((payload.records || []).length) {
      markOnboardingStepComplete("audit_viewer");
    }
  } catch (error) {
    elements.auditList.innerHTML = `<p class="empty-state">${getLabel("errors", "history_failed", "History failed to load")}: ${error.message}</p>`;
  } finally {
    elements.refreshAuditButton.disabled = false;
    elements.refreshAuditButton.textContent = getLabel("controls", "refresh_audit", "Refresh audit view");
  }
}

async function loadShellContent() {
  const [content, providerStatus, assistantState] = await Promise.all([
    fetchJson("/v1/demo-ui/content", { lang: currentLang }),
    fetchJson("/v1/demo-ui/provider-status", { lang: currentLang }),
    fetchJson("/v1/demo-ui/assistant-capabilities", { lang: currentLang }),
  ]);

  currentLang = content.language?.selected || currentLang;
  applyChromeLabels(content.ui_labels);
  renderLanguageOptions(content.language);
  renderOnboarding(content.onboarding);

  cachedScenarios = content.demo.scenarios;
  cachedIntegrationExamples = content.safe_integration.examples;
  cachedReferenceFlows = content.reference_product.flows;

  elements.identitySummary.textContent = `${content.identity.name}: ${content.identity.positioning}`;
  elements.identitySubtext.textContent = `${content.identity.summary} ${content.overview.subtext}`;

  renderStatusChips(content.identity.status);
  renderCapabilities(content.capabilities);
  renderReferenceProductOverview(content.reference_product);
  renderProductShellContent(content.product_shell);
  renderReferenceFlowOptions(cachedReferenceFlows);
  renderDecisionCards(cachedScenarios);
  renderIntegrationOverview(content.safe_integration);
  renderArchitecture(content.architecture);
  renderScope(content.scope);
  renderAudiences(content.audiences);
  renderRoadmap(content.roadmap);
  renderScenarioOptions(cachedScenarios);
  renderIntegrationOptions(cachedIntegrationExamples);
  renderProviderStatus(providerStatus);
  renderAssistantPanel(content.assistant, assistantState);
  await refreshProductShell();
}

async function changeLanguage(lang) {
  currentLang = lang || DEFAULT_LANG;
  storeLang(currentLang);
  await loadShellContent();
  markOnboardingStepComplete("language");
}

elements.referenceFlowButton.addEventListener("click", () => runReferenceProductFlow(elements.referenceFlowSelect.value));
elements.runButton.addEventListener("click", () => runScenario(elements.scenarioSelect.value));
elements.integrationButton.addEventListener("click", () => runIntegrationExample(elements.integrationSelect.value));
elements.refreshHistoryButton.addEventListener("click", () => refreshRunHistory());
elements.refreshAuditButton.addEventListener("click", () => refreshAuditView());
elements.assistantRunInsight.addEventListener("click", () => requestAssistantInsight());
elements.onboardingMarkComplete.addEventListener("click", () => markOnboardingStepComplete(onboardingState.currentStepId));
elements.onboardingNextStep.addEventListener("click", () => {
  const currentStepId = onboardingState.currentStepId;
  if (!currentStepId) {
    return;
  }
  if (!onboardingState.completed.includes(currentStepId)) {
    markOnboardingStepComplete(currentStepId);
    return;
  }
  selectOnboardingStep(findNextOnboardingStep(currentStepId));
});
elements.onboardingReset.addEventListener("click", () => resetOnboarding());
elements.languageSelect.addEventListener("change", (event) => {
  changeLanguage(event.target.value).catch((error) => {
    elements.identitySummary.textContent = getLabel("errors", "ui_load_failed", "SafeCore Product Shell failed to load.");
    elements.identitySubtext.textContent = error.message;
  });
});

loadShellContent().catch((error) => {
  elements.identitySummary.textContent = "SafeCore Product Shell failed to load.";
  elements.identitySubtext.textContent = error.message;
});
