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
    enterLoginOrEmailToResend: string
    unexpectedResendConfirmation: string
    unexpectedSignin: string
    unexpectedDemo: string
    unexpectedRecovery: string
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
    loading: string
    reloadLastSaved: string
    noSession: string
    goToLogin: string
  }
  finance: {
    title: string
    subtitle: string
    autoImportSectionTitle: string
    autoImportSectionSubtitle: string
    assistantStepDownloadTitle: string
    assistantStepOpenTitle: string
    assistantStepTrackTitle: string
    autoImportButton: string
    autoImporting: string
    autoImportDesktopNotice: string
    autoImportMobileNotice: string
    autoImportTokenLabel: string
    autoImportExpiresLabel: string
    autoImportHelper: string
    assistantDownloadButton: string
    assistantDownloadHint: string
    assistantWindowsPreparing: string
    assistantStepsTitle: string
    assistantStep1: string
    assistantStep2: string
    assistantStep3: string
    advancedModeLabel: string
    advancedModeHint: string
    copyConnectionCodeButton: string
    tokenHidden: string
    copiedToast: string
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
    annualAnalysis: string
    noAnnualData: string
    payStubBatch: string
    batchProcessingProgressLabel: string
    salaryTrendExplainer: string
  }
  history: {
    title: string
    subtitle: string
    statusSaved: string
    waitingForPdf: string
    documents: string
    demoDashboard: string
    viewOnly: string
    addDocuments: string
    uploadDocuments: string
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
      ptTitle: "Trocar para portuguÃªs",
      enTitle: "Mudar para inglÃªs",
    },
    authHero: {
      signUpLabel: "Cadastro",
      alreadyHaveAccount: "JÃ¡ tem uma conta? Entre aqui.",
      enterDemo: "Entrar na demo com dados de exemplo",
      enteringDemo: "Entrando na demo...",
      signIn: "Entrar",
      subtitle: "GestÃ£o de Carreira",
      titleLine1: "GestÃ£o",
      titleLine2: "de Carreira",
      description:
        "Crie sua conta para acompanhar sua evoluÃ§Ã£o profissional com mais organizaÃ§Ã£o e clareza.",
    },
    authCard: {
      access: "Acesso",
      signIn: "Entrar",
      createAccount: "Criar conta",
      loginOrEmail: "Login ou e-mail",
      password: "Senha",
      signingIn: "Entrando...",
      forgotPassword: "Esqueci minha senha",
      didNotReceiveEmail: "NÃ£o recebeu o e-mail?",
      resendConfirmation: "Reenviar confirmaÃ§Ã£o",
      afterSignIn: "Depois de entrar, vocÃª serÃ¡ levado para a sua pÃ¡gina.",
      accessHelp: "Ajuda de acesso",
      back: "Voltar",
      enterEmailOnly: "Digite apenas o seu e-mail. Se ele estiver cadastrado, vocÃª receberÃ¡ um link para criar uma nova senha.",
      sendLink: "Enviar link",
      sendingLink: "Enviando...",
      enterLoginOrEmailToResend: "Digite seu login ou e-mail para reenviar a confirmaÃ§Ã£o.",
      unexpectedResendConfirmation: "Falha inesperada ao reenviar a confirmaÃ§Ã£o.",
      unexpectedSignin: "Falha inesperada ao entrar.",
      unexpectedDemo: "Falha inesperada ao abrir a demo.",
      unexpectedRecovery: "Falha inesperada ao recuperar a senha.",
    },
    registerForm: {
      newUser: "Novo usuÃ¡rio",
      accessDetails: "Dados de acesso",
      fullName: "Nome completo",
      nickname: "Apelido (opcional)",
      confirmationEmail: "E-mail de confirmaÃ§Ã£o",
      startDate: "Data de inÃ­cio",
      login: "Login",
      password: "Senha",
      saving: "Salvando...",
      createAccount: "Criar conta",
      afterRegistration: "Depois do cadastro, vocÃª receberÃ¡ um e-mail para confirmar o acesso.",
      requiredFields: "Preencha nome, e-mail, data de exercÃ­cio, login e senha.",
      passwordMinLength: "A senha precisa ter pelo menos 6 caracteres.",
      successMessage: "Cadastro concluÃ­do com sucesso. Agora vocÃª pode entrar com seu login.",
      unexpectedSave: "Falha inesperada ao salvar.",
    },
    dashboard: {
      careerDashboard: "Painel de carreira",
      careerProgressionAnalytics: "AnÃ¡lise de progressÃ£o de carreira",
      demoActive: "DEMO ATIVA",
      loadingSessionData: "Carregando dados da sessÃ£o...",
      noActiveSession: "Nenhuma sessÃ£o ativa foi encontrada. Entre novamente para ver seus dados.",
      goToLogin: "Ir para login",
      profile: "Perfil",
      history: "HistÃ³rico funcional",
      finance: "Financeiro",
      exit: "Sair",
      exitDemo: "Sair da demo",
      exitLabel: "Saindo...",
      loading: "Carregando...",
      tryAgain: "Tentar novamente",
      removeLastRecord: "Remover Ãºltimo registro",
      professionalProfile: "Perfil profissional",
      confirmed: "Confirmado",
      pending: "Pendente",
      profileOverview: "VisÃ£o geral do perfil",
      careerHistory: "HistÃ³rico funcional",
      dataManagement: "GestÃ£o de dados",
      saved: "Salvo",
      waitingForPdf: "Aguardando PDF",
      yearsWorked: "Anos trabalhados",
      events: "Eventos",
      nextProgression: "PrÃ³xima progressÃ£o",
      retirementEstimate: "Estimativa de aposentadoria",
      email: "E-mail",
      level: "NÃ­vel",
      grade: "Classe",
      demoHighlights: "Destaques da demo",
      viewOnly: "Somente visualizaÃ§Ã£o",
      reloadLastSaved: "Recarregar Ãºltimo salvo",
      noSession: "Nenhuma sessÃ£o ativa foi encontrada. Entre novamente para ver seus dados.",
    },
    finance: {
      title: "FinanÃ§as",
      subtitle:
        "Envie um ou mais contracheques e acompanhe o progresso do lote enquanto os arquivos são processados.",
      autoImportSectionTitle: "Importação automática de contracheques",
      autoImportSectionSubtitle:
        "Baixe o assistente no seu computador e siga o passo a passo. Ele abrirá o portal oficial para você fazer login com segurança.",
      autoImportButton: "Iniciar importação",
      autoImporting: "Baixando assistente...",
      autoImportDesktopNotice: "O assistente para Windows ainda está sendo preparado.",
      autoImportMobileNotice: "No celular, volte ao computador para usar o assistente.",
      autoImportTokenLabel: "Código de conexão",
      autoImportExpiresLabel: "Expira em",
      autoImportHelper: "Abra as opções avançadas somente se precisar copiar o código manualmente.",
      assistantDownloadButton: "Baixar para Windows",
      assistantDownloadHint: "O assistente para Windows ainda está sendo preparado.",
      assistantWindowsPreparing: "Assistente Windows em preparação.",
      assistantStepsTitle: "Etapas",
      assistantStep1: "Instale o assistente no Windows.",
      assistantStep2: "Depois de baixar, abra o programa no seu computador.",
      assistantStep3: "Faça login no portal oficial e aguarde os contracheques serem enviados para sua conta.",
      advancedModeLabel: "Opções avançadas",
      advancedModeHint: "Use apenas se precisar copiar o código manualmente ou conferir a validade.",
      tokenHidden: "Cópia protegida.",
      copiedToast: "Assistente baixado. Abra o arquivo para continuar.",
      batchTitle: "Lote de contracheques",
      uploadPdfs: "Enviar PDFs",
      demoDataOnly: "Apenas dados de demo",
      pdfFiles: "Arquivos PDF",
      selectOneOrMorePdfs: "Selecione um ou mais PDFs. O acompanhamento será atualizado automaticamente.",
      demoReadOnly: "A demo mantÃ©m esta seÃ§Ã£o somente leitura porque a anÃ¡lise financeira jÃ¡ estÃ¡ carregada.",
      largeBatchesCanTakeAWhile: "Lotes grandes podem levar alguns minutos. O processamento continua em segundo plano.",
      selectedPdfs: "PDFs selecionados",
      totalSize: "Tamanho total",
      viewDetails: "Ver detalhes",
      fileNamesStayCollapsed: "Os nomes dos arquivos ficam recolhidos para a pÃ¡gina continuar leve mesmo com lotes grandes.",
      additionalFilesHidden: "arquivos adicionais ficam ocultos da prÃ©via.",
      ready: "Pronto",
      uploadingBatch: "Enviando lote...",
      pollingEveryTwoSeconds: "Consultando a cada 2 segundos...",
      waitingForBatchToStart: "Aguardando o lote comeÃ§ar...",
      sendingBatch: "Enviando lote...",
      demoMode: "Modo demo",
      analyzeBatch: "Analisar lote",
      batchMonitor: "Monitor do lote",
      processingStatus: "Status do processamento",
      batchProgressSubtitle: "Uma barra de progresso compacta se atualiza automaticamente enquanto cada PDF é processado.",
      status: "Status",
      processed: "Processados",
      duplicated: "Duplicados",
      failed: "Falharam",
      total: "Total",
      somePaychecksAlreadyExisted: "Alguns contracheques jÃ¡ existiam e foram ignorados.",
      workerKeptGoingAfterFailures: "O processamento continuou mesmo após falhas, então o lote ainda pode terminar com resultados parciais.",
      primaryIssue: "Problema principal",
      primaryIssueNotAvailable: "Problema principal indisponÃ­vel.",
      annualSalaryEvolution: "EvoluÃ§Ã£o salarial anual",
      savedSalaryAnalysis: "AnÃ¡lise salarial salva",
      salaryAnalysisPersists: "Esta seção carrega automaticamente os seus contracheques salvos.",
      demoFigures:
        "Os nÃºmeros da demo sÃ£o estimados a partir dos contracheques de 2015 e 2026 que vocÃª compartilhou, para explorar a tendÃªncia salarial sem enviar arquivos.",
      loadingSavedAnalysis: "Carregando sua análise salva...",
      noPaychecksYet: "VocÃª ainda nÃ£o enviou contracheques.",
      analysisPeriod: "PerÃ­odo de anÃ¡lise",
      startingSalaryBase: "Base salarial inicial",
      endingSalaryBase: "Base salarial final",
      salaryBaseEvolution: "EvoluÃ§Ã£o da base salarial",
      salaryBaseByYear: "Base salarial por ano",
      grossTotalAndNetPay: "Bruto total e lÃ­quido",
      grossAndNetSubtitle: "O segundo grÃ¡fico mantÃ©m os valores bruto e lÃ­quido separados sem empilhar blocos.",
      discounts: "Descontos",
      annualSummaryTable: "Tabela anual resumida",
      summaryKeepsDeductionsReadable: "O resumo mantÃ©m os descontos legÃ­veis sem adicionar outro grÃ¡fico pesado.",
      year: "Ano",
      pension: "PrevidÃªncia",
      irrf: "IRRF",
      loans: "EmprÃ©stimos",
      health: "SaÃºde",
      otherDiscounts: "Outros descontos",
      totalLabel: "Total",
      yearsWithoutRelevantGrowth: "Anos sem crescimento relevante",
      annualAnalysis: "AnÃ¡lise anual",
      noAnnualData: "Ainda nÃ£o hÃ¡ dados anuais disponÃ­veis.",
      payStubBatch: "AnÃ¡lise financeira em lote",
      batchProcessingProgressLabel: "Progresso do processamento do lote",
      salaryTrendExplainer: "Uma linha única mantém a tendência salarial clara e fácil de acompanhar.",
    },
    history: {
      title: "HistÃ³rico funcional",
      subtitle:
        "Envie um ou mais contracheques e acompanhe o progresso do lote enquanto os arquivos são processados.",
      statusSaved: "Salvo",
      waitingForPdf: "Aguardando PDF",
      documents: "Documentos",
      demoDashboard: "Painel de demonstraÃ§Ã£o",
      viewOnly: "Somente visualizaÃ§Ã£o",
      addDocuments: "Adicionar documentos",
      uploadDocuments: "Enviar documentos",
      uploadCareerHistory: "Enviar histÃ³rico funcional",
      attachLeaveRecords: "Anexar afastamentos",
      updateCareerHistory: "Atualizar histÃ³rico funcional",
      downloadPdf: "Baixar PDF",
      demoDataLoaded: "Os dados abaixo jÃ¡ estÃ£o carregados para a demo.",
      openAccount: "Abrir conta",
      opening: "Abrindo...",
      clickUploadCareerHistory: "Clique em \"Enviar histÃ³rico funcional\" para abrir os campos de upload.",
      careerHistoryPdf: "PDF do histÃ³rico funcional",
      dateOfBirth: "Data de nascimento",
      recognizedCltYears: "Anos CLT reconhecidos",
      leaveRecordsPdf: "PDF de afastamentos",
      selectedLeaveRecordsFile: "Arquivo de afastamentos selecionado",
      fill10CltYears: "Preencher 10 anos CLT",
      upTo10CltYears: "VocÃª pode informar atÃ© 10 anos CLT. Se jÃ¡ tiver esse tempo, digite 10 ou use o atalho.",
      selectedFile: "Arquivo selecionado",
      reloadLastSaved: "Recarregar Ãºltimo salvo",
      selectPdfToAttach: "Selecione o PDF para anexar aos dados salvos.",
      sendOtherFiles: "Para enviar outros arquivos, use os botÃµes acima para abrir o campo correspondente.",
      pdfStorage: "Armazenamento do PDF",
      processing: "Processamento",
      timeWorked: "Tempo trabalhado",
      timeRemaining: "Tempo restante",
      events: "Eventos",
      daysAway: "Dias afastado",
      medicalReview: "RevisÃ£o mÃ©dica",
      nextProgression: "PrÃ³xima progressÃ£o",
      comparison: "ComparaÃ§Ã£o",
      timeWorkedAndLeave: "Tempo trabalhado e afastamento",
      noLeavePeriods: "VocÃª nÃ£o possui perÃ­odos de afastamento registrados para desenhar a comparaÃ§Ã£o.",
      start: "InÃ­cio",
      today: "Hoje",
      data: "Data",
      delayed: "Atrasado",
      probation: "ProbatÃ³rio",
      onTrack: "Em dia",
      nA: "N/A",
      medicalLeave: "LicenÃ§a mÃ©dica",
      medicalReviewCompleted: "RevisÃ£o mÃ©dica concluÃ­da",
      daysUntilMedicalReview: "dias atÃ© a revisÃ£o mÃ©dica",
      enoughEvents: "O PDF nÃ£o trouxe eventos suficientes para desenhar a linha do tempo.",
      chartTitle: "Linha do tempo de progressÃµes e promoÃ§Ãµes",
      uploadHint: "Envie o PDF do histÃ³rico funcional para analisar os dados e montar os cÃ¡lculos de carreira.",
      loadedInDemo: "Aqui vocÃª verÃ¡ tempo trabalhado, projeÃ§Ã£o de aposentadoria e a prÃ³xima progressÃ£o e promoÃ§Ã£o.",
      userRequiredForHistory: "Crie um usuÃ¡rio antes de enviar o histÃ³rico funcional.",
      userRequiredForLeave: "Crie um usuÃ¡rio antes de enviar afastamentos.",
      chooseCareerHistoryPdf: "Escolha um PDF do histÃ³rico funcional.",
      chooseLeaveRecordsPdf: "Escolha um PDF de afastamentos.",
      processingCareerHistory: "Processando o PDF do histÃ³rico funcional em segundo plano...",
      processingLeaveRecords: "Processando o PDF de afastamentos em segundo plano...",
      unexpectedReload: "Falha inesperada ao recarregar.",
      unexpectedAnalyze: "Falha inesperada ao analisar.",
      unexpectedAttach: "Falha inesperada ao analisar afastamentos.",
      loadSavedAnalysis: "Carregar anÃ¡lise salva",
      uploadFilesAbove: "Para enviar outros arquivos, use os botÃµes acima para abrir o campo correspondente.",
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
      subtitle:
        "Envie um ou mais contracheques e acompanhe o progresso do lote enquanto os arquivos são processados.",
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
      enterLoginOrEmailToResend: "Enter your login or email to resend the confirmation.",
      unexpectedResendConfirmation: "Unexpected failure while resending the confirmation.",
      unexpectedSignin: "Unexpected failure while signing in.",
      unexpectedDemo: "Unexpected failure while opening the demo.",
      unexpectedRecovery: "Unexpected failure while recovering the password.",
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
      requiredFields: "Fill in name, email, start date, login, and password.",
      passwordMinLength: "The password must be at least 6 characters long.",
      successMessage: "Registration completed successfully. You can now sign in with your login.",
      unexpectedSave: "Unexpected failure while saving.",
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
      yearsWorked: "Years Worked",
      events: "Events",
      nextProgression: "Next Progression",
      retirementEstimate: "Retirement Estimate",
      email: "Email",
      level: "Level",
      grade: "Grade",
      demoHighlights: "Demo Highlights",
      viewOnly: "View Only",
      loading: "Loading...",
      reloadLastSaved: "Reload Last Saved",
      noSession: "No active session was found. Sign in again to view your data.",
      goToLogin: "Go to Login",
    },
    finance: {
      title: "Finance",
      subtitle:
        "Upload one or more pay stubs, then watch the batch progress as the files are processed.",
      autoImportSectionTitle: "Automatic pay stub import",
      autoImportSectionSubtitle:
        "Download the assistant on your computer and follow the steps. It will open the official portal so you can sign in securely.",
      autoImportButton: "Start import",
      autoImporting: "Downloading assistant...",
      autoImportDesktopNotice: "The Windows assistant is still being prepared.",
      autoImportMobileNotice: "On mobile, return to a computer to use the assistant.",
      autoImportTokenLabel: "Connection code",
      autoImportExpiresLabel: "Expires at",
      autoImportHelper: "Open advanced options only if you need to copy the code manually.",
      assistantDownloadButton: "Download for Windows",
      assistantDownloadHint: "The Windows assistant is still being prepared.",
      assistantWindowsPreparing: "Windows assistant is being prepared.",
      assistantStepsTitle: "Steps",
      assistantStep1: "Install the assistant on Windows.",
      assistantStep2: "After downloading, open the program on your computer.",
      assistantStep3: "Sign in on the official portal and wait for the pay stubs to be sent to your account.",
      advancedModeLabel: "Advanced options",
      advancedModeHint: "Use only if you need to copy the code manually or check its validity.",
      tokenHidden: "Protected copy.",
      copiedToast: "Assistant downloaded. Open the file to continue.",
      batchTitle: "Pay Stub Batch",
      uploadPdfs: "Upload PDFs",
      demoDataOnly: "Demo data only",
      pdfFiles: "PDF files",
      selectOneOrMorePdfs: "Select one or more PDFs. The progress will update automatically.",
      demoReadOnly: "Demo mode keeps this section read-only because the financial analysis is already loaded.",
      largeBatchesCanTakeAWhile: "Large batches can take a few minutes. Processing continues in the background.",
      selectedPdfs: "Selected PDFs",
      totalSize: "Total size",
      viewDetails: "View details",
      fileNamesStayCollapsed: "File names stay collapsed so the page stays light even with large batches.",
      additionalFilesHidden: "additional files are hidden from the preview.",
      ready: "Ready",
      uploadingBatch: "Uploading batch...",
      pollingEveryTwoSeconds: "Polling every 2 seconds...",
      waitingForBatchToStart: "Waiting for the batch to start...",
      sendingBatch: "Sending batch...",
      demoMode: "Demo mode",
      analyzeBatch: "Analyze batch",
      batchMonitor: "Batch Monitor",
      processingStatus: "Processing status",
      batchProgressSubtitle: "A compact progress bar updates automatically while each uploaded PDF is processed.",
      status: "Status",
      processed: "Processed",
      duplicated: "Duplicated",
      failed: "Failed",
      total: "Total",
      somePaychecksAlreadyExisted: "Some paychecks already existed and were ignored.",
      workerKeptGoingAfterFailures: "Processing continued after failures, so the batch can still finish with partial results.",
      primaryIssue: "Primary issue",
      primaryIssueNotAvailable: "Primary issue not available.",
      annualSalaryEvolution: "Annual Salary Evolution",
      savedSalaryAnalysis: "Saved salary analysis",
      salaryAnalysisPersists: "This section automatically loads your saved paychecks.",
      demoFigures:
        "Demo figures are estimated from the 2015 and 2026 pay stubs you shared, so you can explore the salary trend without uploading files.",
      loadingSavedAnalysis: "Loading your saved analysis...",
      noPaychecksYet: "You have not uploaded any pay stubs yet.",
      analysisPeriod: "Analysis period",
      startingSalaryBase: "Starting salary base",
      endingSalaryBase: "Ending salary base",
      salaryBaseEvolution: "Salary base evolution",
      salaryBaseByYear: "Salary base by year",
      grossTotalAndNetPay: "Gross total and net pay",
      grossAndNetSubtitle: "The second line chart keeps gross and liquid values separated without stacking blocks.",
      discounts: "Discounts",
      annualSummaryTable: "Annual summary table",
      summaryKeepsDeductionsReadable: "The summary keeps deductions readable without adding another heavy chart.",
      year: "Year",
      pension: "Pension",
      irrf: "IRRF",
      loans: "Loans",
      health: "Health",
      otherDiscounts: "Other discounts",
      totalLabel: "Total",
      yearsWithoutRelevantGrowth: "Years without relevant growth",
      annualAnalysis: "Annual analysis",
      noAnnualData: "No annual data is available yet.",
      payStubBatch: "Batch financial analysis",
      batchProcessingProgressLabel: "Batch processing progress",
      salaryTrendExplainer: "A single line keeps the salary trend clear and easy to follow.",
    },
    history: {
      title: "Career History",
      subtitle:
        "Upload one or more pay stubs, then watch the batch progress as the files are processed.",
      statusSaved: "Saved",
      waitingForPdf: "Waiting for PDF",
      documents: "Documents",
      demoDashboard: "Demo Dashboard",
      viewOnly: "View Only",
      addDocuments: "Add Documents",
      uploadDocuments: "Upload Documents",
      uploadCareerHistory: "Upload Career History",
      attachLeaveRecords: "Attach Leave Records",
      updateCareerHistory: "Update Career History",
      downloadPdf: "Download PDF",
      demoDataLoaded: "The data below is already loaded for the demo.",
      openAccount: "Create Account",
      opening: "Opening...",
      clickUploadCareerHistory: 'Click "Upload Career History" to open the upload fields.',
      careerHistoryPdf: "Career History PDF",
      dateOfBirth: "Date of Birth",
      recognizedCltYears: "Recognized CLT Years",
      leaveRecordsPdf: "Leave Records PDF",
      selectedLeaveRecordsFile: "Selected leave records file",
      fill10CltYears: "Fill 10 CLT Years",
      upTo10CltYears: "You can enter up to 10 CLT years. If you already have that time, enter 10 or use the shortcut.",
      selectedFile: "Selected file",
      reloadLastSaved: "Reload Last Saved",
      selectPdfToAttach: "Select the PDF to attach to the saved data.",
      sendOtherFiles: "To send other files, use the buttons above to open the corresponding field.",
      pdfStorage: "PDF storage",
      processing: "Processing",
      timeWorked: "Time Worked",
      timeRemaining: "Time Remaining",
      events: "Events",
      daysAway: "Days Away",
      medicalReview: "Medical Review",
      nextProgression: "Next Progression",
      comparison: "Comparison",
      timeWorkedAndLeave: "Time Worked and Leave",
      noLeavePeriods: "You do not have any recorded leave periods to draw the comparison.",
      start: "Start",
      today: "Today",
      data: "Date",
      delayed: "Delayed",
      probation: "Probation",
      onTrack: "On Track",
      nA: "N/A",
      medicalLeave: "Medical Leave",
      medicalReviewCompleted: "Medical review completed",
      daysUntilMedicalReview: "days until medical review",
      enoughEvents: "The PDF did not bring enough events to draw the timeline.",
      chartTitle: "Timeline of progressions and promotions",
      uploadHint: "Upload the career history PDF to analyze the data and build the career calculations.",
      loadedInDemo: "Here you will see time worked, retirement projection, and the next progression and promotion.",
      userRequiredForHistory: "Create a user before uploading the career history.",
      userRequiredForLeave: "Create a user before uploading leave records.",
      chooseCareerHistoryPdf: "Choose a career history PDF.",
      chooseLeaveRecordsPdf: "Choose a leave records PDF.",
      processingCareerHistory: "Processing the career history PDF in the background...",
      processingLeaveRecords: "Processing the leave records PDF in the background...",
      unexpectedReload: "Unexpected failure while reloading.",
      unexpectedAnalyze: "Unexpected failure while analyzing.",
      unexpectedAttach: "Unexpected failure while analyzing leave records.",
      loadSavedAnalysis: "Load saved analysis",
      uploadFilesAbove: "To send other files, use the buttons above to open the corresponding field.",
    },
  },
}

export function normalizarIdioma(valor: string | null | undefined): SiteLanguage {
  return valor === "en" ? "en" : "pt-BR"
}

export function serializarCookieIdioma(idioma: SiteLanguage) {
  return `${SITE_LANGUAGE_COOKIE_NAME}=${encodeURIComponent(idioma)}; Path=/; Max-Age=${LANGUAGE_COOKIE_MAX_AGE}; SameSite=Lax`
}
