export type SiteLanguage = "pt-BR" | "en"

export const SITE_LANGUAGE_COOKIE_NAME = "career-language"
export const SITE_LANGUAGE_STORAGE_KEY = "career-language"
const LANGUAGE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

export type LocaleTexts = {
  theme: {
    label: string
    lightTitle: string
    darkTitle: string
    lightState: string
    darkState: string
  }
  language: {
    label: string
    ptState: string
    enState: string
    ptTitle: string
    enTitle: string
  }
  authHero: {
    signUpLabel: string
    alreadyHaveAccount: string
    enterDemo: string
    enteringDemo: string
    signIn: string
    subtitle: string
    titleLine1: string
    titleLine2: string
    description: string
  }
  authCard: {
    access: string
    signIn: string
    createAccount: string
    loginOrEmail: string
    password: string
    signingIn: string
    forgotPassword: string
    didNotReceiveEmail: string
    resendConfirmation: string
    afterSignIn: string
    accessHelp: string
    back: string
    enterEmailOnly: string
    sendLink: string
    sendingLink: string
  }
  registerForm: {
    newUser: string
    accessDetails: string
    fullName: string
    nickname: string
    confirmationEmail: string
    startDate: string
    login: string
    password: string
    saving: string
    createAccount: string
    afterRegistration: string
    requiredFields: string
    passwordMinLength: string
    successMessage: string
    unexpectedSave: string
  }
  dashboard: {
    careerDashboard: string
    careerProgressionAnalytics: string
    demoActive: string
    loadingSessionData: string
    noActiveSession: string
    goToLogin: string
    profile: string
    history: string
    finance: string
    exit: string
    exitDemo: string
    exitLabel: string
    loading: string
    tryAgain: string
    removeLastRecord: string
    professionalProfile: string
    confirmed: string
    pending: string
    profileOverview: string
    careerHistory: string
    dataManagement: string
    saved: string
    waitingForPdf: string
    yearsWorked: string
    events: string
    nextProgression: string
    retirementEstimate: string
    email: string
    level: string
    grade: string
    demoHighlights: string
    viewOnly: string
    addDocuments: string
    uploadDocuments: string
    loading: string
    reloadLastSaved: string
    noSession: string
    goToLogin: string
  }
  finance: {
    title: string
    subtitle: string
    batchTitle: string
    uploadPdfs: string
    demoDataOnly: string
    pdfFiles: string
    selectOneOrMorePdfs: string
    demoReadOnly: string
    largeBatchesCanTakeAWhile: string
    selectedPdfs: string
    totalSize: string
    viewDetails: string
    fileNamesStayCollapsed: string
    additionalFilesHidden: string
    ready: string
    uploadingBatch: string
    pollingEveryTwoSeconds: string
    waitingForBatchToStart: string
    sendingBatch: string
    demoMode: string
    analyzeBatch: string
    batchMonitor: string
    processingStatus: string
    batchProgressSubtitle: string
    status: string
    processed: string
    duplicated: string
    failed: string
    total: string
    somePaychecksAlreadyExisted: string
    workerKeptGoingAfterFailures: string
    primaryIssue: string
    primaryIssueNotAvailable: string
    annualSalaryEvolution: string
    savedSalaryAnalysis: string
    salaryAnalysisPersists: string
    demoFigures: string
    loadingSavedAnalysis: string
    noPaychecksYet: string
    analysisPeriod: string
    startingSalaryBase: string
    endingSalaryBase: string
    salaryBaseEvolution: string
    salaryBaseByYear: string
    grossTotalAndNetPay: string
    grossAndNetSubtitle: string
    discounts: string
    annualSummaryTable: string
    summaryKeepsDeductionsReadable: string
    year: string
    pension: string
    irrf: string
    loans: string
    health: string
    otherDiscounts: string
    totalLabel: string
    yearsWithoutRelevantGrowth: string
  }
  history: {
    title: string
    subtitle: string
    statusSaved: string
    waitingForPdf: string
    documents: string
    demoDashboard: string
    viewOnly: string
    uploadCareerHistory: string
    attachLeaveRecords: string
    updateCareerHistory: string
    downloadPdf: string
    demoDataLoaded: string
    openAccount: string
    opening: string
    clickUploadCareerHistory: string
    careerHistoryPdf: string
    dateOfBirth: string
    recognizedCltYears: string
    leaveRecordsPdf: string
    selectedLeaveRecordsFile: string
    fill10CltYears: string
    upTo10CltYears: string
    selectedFile: string
    reloadLastSaved: string
    selectPdfToAttach: string
    sendOtherFiles: string
    pdfStorage: string
    processing: string
    timeWorked: string
    timeRemaining: string
    events: string
    daysAway: string
    medicalReview: string
    nextProgression: string
    comparison: string
    timeWorkedAndLeave: string
    noLeavePeriods: string
    start: string
    today: string
    data: string
    delayed: string
    probation: string
    onTrack: string
    nA: string
    medicalLeave: string
    medicalReviewCompleted: string
    daysUntilMedicalReview: string
    enoughEvents: string
    chartTitle: string
    uploadHint: string
    loadedInDemo: string
    userRequiredForHistory: string
    userRequiredForLeave: string
    chooseCareerHistoryPdf: string
    chooseLeaveRecordsPdf: string
    processingCareerHistory: string
    processingLeaveRecords: string
    unexpectedReload: string
    unexpectedAnalyze: string
    unexpectedAttach: string
    loadSavedAnalysis: string
    uploadFilesAbove: string
  }
}

export const LOCALE_TEXTS: Record<SiteLanguage, LocaleTexts> = {
  "pt-BR": {
    theme: {
      label: "Tema",
      lightTitle: "Ativar tema claro",
      darkTitle: "Ativar tema escuro",
      lightState: "Claro",
      darkState: "Escuro",
    },
    language: {
      label: "Idioma",
      ptState: "PT",
      enState: "EN",
      ptTitle: "Trocar para português",
      enTitle: "Mudar para inglês",
    },
    authHero: {
      signUpLabel: "Cadastro",
      alreadyHaveAccount: "Já tem uma conta? Entre aqui.",
      enterDemo: "Entrar na demo com dados de exemplo",
      enteringDemo: "Entrando na demo...",
      signIn: "Entrar",
      subtitle: "Gestão de Carreira",
      titleLine1: "Gestão",
      titleLine2: "de Carreira",
      description:
        "Crie sua conta para acompanhar sua evolução profissional com mais organização e clareza.",
    },
    authCard: {
      access: "Acesso",
      signIn: "Entrar",
      createAccount: "Criar conta",
      loginOrEmail: "Login ou e-mail",
      password: "Senha",
      signingIn: "Entrando...",
      forgotPassword: "Esqueci minha senha",
      didNotReceiveEmail: "Não recebeu o e-mail?",
      resendConfirmation: "Reenviar confirmação",
      afterSignIn: "Depois de entrar, você será levado para a sua página.",
      accessHelp: "Ajuda de acesso",
      back: "Voltar",
      enterEmailOnly: "Digite apenas o seu e-mail. Se ele estiver cadastrado, você receberá um link para criar uma nova senha.",
      sendLink: "Enviar link",
      sendingLink: "Enviando...",
    },
    registerForm: {
      newUser: "Novo usuário",
      accessDetails: "Dados de acesso",
      fullName: "Nome completo",
      nickname: "Apelido (opcional)",
      confirmationEmail: "E-mail de confirmação",
      startDate: "Data de início",
      login: "Login",
      password: "Senha",
      saving: "Salvando...",
      createAccount: "Criar conta",
      afterRegistration: "Depois do cadastro, você receberá um e-mail para confirmar o acesso.",
    },
    dashboard: {
      careerDashboard: "Painel de carreira",
      careerProgressionAnalytics: "Análise de progressão de carreira",
      demoActive: "DEMO ATIVA",
      loadingSessionData: "Carregando dados da sessão...",
      noActiveSession: "Nenhuma sessão ativa foi encontrada. Entre novamente para ver seus dados.",
      goToLogin: "Ir para login",
      profile: "Perfil",
      history: "Histórico funcional",
      finance: "Financeiro",
      exit: "Sair",
      exitDemo: "Sair da demo",
      exitLabel: "Saindo...",
      loading: "Carregando...",
      tryAgain: "Tentar novamente",
      removeLastRecord: "Remover último registro",
      professionalProfile: "Perfil profissional",
      confirmed: "Confirmado",
      pending: "Pendente",
      profileOverview: "Visão geral do perfil",
      careerHistory: "Histórico funcional",
      dataManagement: "Gestão de dados",
      saved: "Salvo",
      waitingForPdf: "Aguardando PDF",
    },
  },
  en: {
    theme: {
      label: "Theme",
      lightTitle: "Turn on light theme",
      darkTitle: "Turn on dark theme",
      lightState: "Light",
      darkState: "Dark",
    },
    language: {
      label: "Language",
      ptState: "PT",
      enState: "EN",
      ptTitle: "Switch to Portuguese",
      enTitle: "Switch to English",
    },
    authHero: {
      signUpLabel: "Sign Up",
      alreadyHaveAccount: "Already have an account? Sign in here.",
      enterDemo: "Enter demo with sample data",
      enteringDemo: "Entering demo...",
      signIn: "Sign In",
      subtitle: "CareerFlow",
      titleLine1: "Career",
      titleLine2: "Flow",
      description:
        "Create your account to keep track of your career progression with more clarity and organization.",
    },
    authCard: {
      access: "Access",
      signIn: "Sign In",
      createAccount: "Create Account",
      loginOrEmail: "Login or Email",
      password: "Password",
      signingIn: "Signing in...",
      forgotPassword: "Forgot Password",
      didNotReceiveEmail: "Didn't receive the email?",
      resendConfirmation: "Resend Confirmation Email",
      afterSignIn: "After signing in, you'll go to your page.",
      accessHelp: "Access Help",
      back: "Back",
      enterEmailOnly: "Enter only your email. If it is registered, you will receive a link to create a new password.",
      sendLink: "Send Link",
      sendingLink: "Sending...",
    },
    registerForm: {
      newUser: "New User",
      accessDetails: "Access Details",
      fullName: "Full Name",
      nickname: "Nickname (optional)",
      confirmationEmail: "Confirmation Email",
      startDate: "Start Date",
      login: "Login",
      password: "Password",
      saving: "Saving...",
      createAccount: "Create Account",
      afterRegistration: "After registration, you will receive an email to confirm access.",
    },
    dashboard: {
      careerDashboard: "Career Dashboard",
      careerProgressionAnalytics: "Career Progression Analytics",
      demoActive: "DEMO ACTIVE",
      loadingSessionData: "Loading session data...",
      noActiveSession: "No active session was found. Sign in again to view your data.",
      goToLogin: "Go to Login",
      profile: "Profile",
      history: "Career History",
      finance: "Finance",
      exit: "Exit",
      exitDemo: "Exit Demo",
      exitLabel: "Exiting...",
      loading: "Loading...",
      tryAgain: "Try again",
      removeLastRecord: "Clear Last Record",
      professionalProfile: "Professional Profile",
      confirmed: "Confirmed",
      pending: "Pending",
      profileOverview: "Profile Overview",
      careerHistory: "Career History",
      dataManagement: "Data Management",
      saved: "Saved",
      waitingForPdf: "Waiting for PDF",
    },
  },
}

export function normalizarIdioma(valor: string | null | undefined): SiteLanguage {
  return valor === "en" ? "en" : "pt-BR"
}

export function serializarCookieIdioma(idioma: SiteLanguage) {
  return `${SITE_LANGUAGE_COOKIE_NAME}=${encodeURIComponent(idioma)}; Path=/; Max-Age=${LANGUAGE_COOKIE_MAX_AGE}; SameSite=Lax`
}
