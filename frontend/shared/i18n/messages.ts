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
    enterDemo: string
    enteringDemo: string
    noAccount: string
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
    resendConfirmation: string
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
    emailAlreadyRegistered: string
    loginAlreadyRegistered: string
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
    fullName: string
    registrationNumber: string
    cpf: string
    birthDate: string
    possessionDate: string
    position: string
    symbol: string
    level: string
    grade: string
    demoHighlights: string
    viewOnly: string
    reloadLastSaved: string
    noSession: string
  }
  finance: {
    title: string
    subtitle: string
    autoImportSectionTitle: string
    autoImportSectionSubtitle: string
    autoImportButton: string
    autoImporting: string
    autoImportDesktopNotice: string
    autoImportMobileNotice: string
    autoImportTokenLabel: string
    autoImportExpiresLabel: string
    autoImportHelper: string
    assistantDownloadButton: string
    assistantDownloadHint: string
    assistantInstallLink: string
    mobileImportNotice: string
    manualTokenReminderText: string
    manualTokenModalTitle: string
    manualTokenModalSubtitle: string
    manualTokenModalHint: string
    tokenCopiedFeedback: string
    closeTokenModalButton: string
    assistantWindowsPreparing: string
    assistantStepsTitle: string
    assistantStep1: string
    assistantStep2: string
    assistantStep3: string
    assistantStep4: string
    generateTemporaryTokenButton: string
    copyTokenButton: string
    assistantLaunchError: string
    assistantLaunchErrorPrefix: string
    assistantLaunchErrorSuffix: string
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
    clearPaychecksButton: string
    clearPaychecksConfirmTitle: string
    clearPaychecksConfirmText: string
    clearPaychecksYes: string
    clearPaychecksNo: string
    clearPaychecksLoading: string
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
      ptTitle: "Trocar para português",
      enTitle: "Mudar para inglês",
    },
    authHero: {
      enterDemo: "Explorar demonstração",
      enteringDemo: "Abrindo demonstração...",
      noAccount: "Não tem conta?",
      titleLine1: "Gestão",
      titleLine2: "de Carreira",
      description:
        "Organize sua evolução profissional com clareza, automação e inteligência.",
    },
    authCard: {
      access: "Acesso",
      signIn: "Entrar",
      createAccount: "Criar conta",
      loginOrEmail: "Login ou e-mail",
      password: "Senha",
      signingIn: "Entrando...",
      forgotPassword: "Esqueci minha senha",
      resendConfirmation: "Reenviar confirmação",
      accessHelp: "Ajuda de acesso",
      back: "Voltar",
      enterEmailOnly: "Digite apenas o seu e-mail. Se ele estiver cadastrado, você receberá um link para criar uma nova senha.",
      sendLink: "Enviar link",
      sendingLink: "Enviando...",
      enterLoginOrEmailToResend: "Digite seu login ou e-mail para reenviar a confirmação.",
      unexpectedResendConfirmation: "Falha inesperada ao reenviar a confirmação.",
      unexpectedSignin: "Falha inesperada ao entrar.",
      unexpectedDemo: "Falha inesperada ao abrir a demo.",
      unexpectedRecovery: "Falha inesperada ao recuperar a senha.",
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
      requiredFields: "Preencha nome, e-mail, data de exercício, login e senha.",
      passwordMinLength: "A senha precisa ter pelo menos 6 caracteres.",
      emailAlreadyRegistered: "Este email já está cadastrado.",
      loginAlreadyRegistered: "Este login já está cadastrado.",
      successMessage: "Cadastro concluído com sucesso. Agora você pode entrar com seu login.",
      unexpectedSave: "Não foi possível criar a conta agora. Tente novamente.",
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
      yearsWorked: "Anos trabalhados",
      events: "Eventos",
      nextProgression: "Próxima progressão",
      retirementEstimate: "Estimativa de aposentadoria",
      email: "E-mail",
      fullName: "Nome completo",
      registrationNumber: "MASP",
      cpf: "CPF",
      birthDate: "Data de nascimento",
      possessionDate: "Data de posse",
      position: "Cargo atual",
      symbol: "Símbolo atual",
      level: "Nível",
      grade: "Classe",
      demoHighlights: "Destaques da demo",
      viewOnly: "Somente visualização",
      reloadLastSaved: "Recarregar último salvo",
      noSession: "Nenhuma sessão ativa foi encontrada. Entre novamente para ver seus dados.",
    },
    finance: {
      title: "Finanças",
      subtitle:
        "Envie um ou mais contracheques e acompanhe o progresso do lote enquanto os arquivos são processados.",
      autoImportSectionTitle: "Abra o assistente para importar seus contracheques",
      autoImportSectionSubtitle:
        "Faça login normalmente no Portal do Servidor. Depois abra a página de contracheques e deixe o resto comigo.",
      autoImportButton: "Abrir assistente agora",
      autoImporting: "Abrindo assistente...",
      autoImportDesktopNotice: "O download para Windows ainda está sendo preparado.",
      autoImportMobileNotice: "No celular, volte ao computador para usar o assistente.",
      autoImportTokenLabel: "Código de conexão",
      autoImportExpiresLabel: "Expira em",
      autoImportHelper: "Use o token manual só se a abertura automática falhar.",
      assistantDownloadButton: "Baixar assistente",
      assistantDownloadHint: "Baixe o instalador para abrir o assistente no seu computador.",
      assistantInstallLink: "Baixe o assistente",
      mobileImportNotice:
        "Não é possível baixar o assistente pelo celular. Use um computador para continuar.",
      manualTokenReminderText:
        "Se a abertura automática não funcionar, gere um token temporário, cole no assistente e pressione Enter.",
      manualTokenModalTitle: "Token temporário",
      manualTokenModalSubtitle:
        "Copie este token e cole no assistente só se a abertura automática falhar.",
      manualTokenModalHint: "Abra o assistente no computador e cole este token apenas se precisar.",
      tokenCopiedFeedback: "Token copiado.",
      closeTokenModalButton: "Fechar",
      assistantWindowsPreparing: "Preparando o download para Windows.",
      assistantStepsTitle: "Como funciona",
      assistantStep1: "Baixe o assistente",
      assistantStep2: "Abra no computador",
      assistantStep3: "Entre com segurança usando gov.br",
      assistantStep4: "Seus contracheques aparecem aqui sem complicação",
      generateTemporaryTokenButton: "Gerar token temporário",
      copyTokenButton: "Copiar token",
      assistantLaunchError: "Não consegui iniciar a importação agora. Tente novamente.",
      assistantLaunchErrorPrefix: "Não consegui abrir o assistente.",
      assistantLaunchErrorSuffix: " e tente novamente.",
      batchTitle: "Lote de contracheques",
      uploadPdfs: "Enviar PDFs",
      demoDataOnly: "Apenas dados de demo",
      pdfFiles: "Arquivos PDF",
      selectOneOrMorePdfs: "Selecione um ou mais PDFs. O acompanhamento será atualizado automaticamente.",
      demoReadOnly: "A demo mantém esta seção somente leitura porque a análise financeira já está carregada.",
      largeBatchesCanTakeAWhile: "Lotes grandes podem levar alguns minutos. O processamento continua em segundo plano.",
      selectedPdfs: "PDFs selecionados",
      totalSize: "Tamanho total",
      viewDetails: "Ver detalhes",
      fileNamesStayCollapsed: "Os nomes dos arquivos ficam recolhidos para a página continuar leve mesmo com lotes grandes.",
      additionalFilesHidden: "arquivos adicionais ficam ocultos da prévia.",
      ready: "Pronto",
      uploadingBatch: "Enviando lote...",
      pollingEveryTwoSeconds: "Consultando a cada 2 segundos...",
      waitingForBatchToStart: "Aguardando o lote começar...",
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
      somePaychecksAlreadyExisted: "Alguns contracheques já existiam e foram ignorados.",
      workerKeptGoingAfterFailures: "O processamento continuou mesmo após falhas, então o lote ainda pode terminar com resultados parciais.",
      missingPaycheckMonthsTitle: "Folhas faltantes",
      missingPaycheckMonthsWarning:
        "Houve um erro ao captar as folhas dos meses {{months}}. Envie manualmente ou veja a análise sem esses meses.",
      primaryIssue: "Problema principal",
      primaryIssueNotAvailable: "Problema principal indisponível.",
      clearPaychecksButton: "Limpar PDFs",
      clearPaychecksConfirmTitle: "Limpar PDFs",
      clearPaychecksConfirmText: "Tem certeza de que deseja apagar todos os contracheques baixados?",
      clearPaychecksYes: "Sim",
      clearPaychecksNo: "Não",
      clearPaychecksLoading: "Apagando...",
      annualSalaryEvolution: "Evolução salarial anual",
      savedSalaryAnalysis: "Análise salarial salva",
      salaryAnalysisPersists: "Esta seção carrega automaticamente os seus contracheques salvos.",
      demoFigures:
        "Os números da demo são estimados a partir dos contracheques de 2015 e 2026 que você compartilhou, para explorar a tendência salarial sem enviar arquivos.",
      loadingSavedAnalysis: "Carregando sua análise salva...",
      noPaychecksYet: "Você ainda não enviou contracheques.",
      analysisPeriod: "Período de análise",
      startingSalaryBase: "Base salarial inicial",
      endingSalaryBase: "Base salarial final",
      salaryBaseEvolution: "Evolução da base salarial",
      salaryBaseByYear: "Base salarial por ano",
      grossTotalAndNetPay: "Bruto total e líquido",
      grossAndNetSubtitle: "O segundo gráfico mantém os valores bruto e líquido separados sem empilhar blocos.",
      discounts: "Descontos",
      annualSummaryTable: "Tabela anual resumida",
      summaryKeepsDeductionsReadable: "O resumo mantém os descontos legíveis sem adicionar outro gráfico pesado.",
      year: "Ano",
      pension: "Previdência",
      irrf: "IRRF",
      loans: "Empréstimos",
      health: "Saúde",
      otherDiscounts: "Outros descontos",
      totalLabel: "Total",
      yearsWithoutRelevantGrowth: "Anos sem crescimento relevante",
      annualAnalysis: "Análise anual",
      noAnnualData: "Ainda não há dados anuais disponíveis.",
      payStubBatch: "Análise financeira em lote",
      batchProcessingProgressLabel: "Progresso do processamento do lote",
      salaryTrendExplainer: "Uma linha única mantém a tendência salarial clara e fácil de acompanhar.",
    },
    history: {
      title: "Histórico funcional",
      subtitle:
        "Envie um ou mais contracheques e acompanhe o progresso do lote enquanto os arquivos são processados.",
      statusSaved: "Salvo",
      waitingForPdf: "Aguardando PDF",
      documents: "Documentos",
      demoDashboard: "Painel de demonstração",
      viewOnly: "Somente visualização",
      addDocuments: "Adicionar documentos",
      uploadDocuments: "Enviar documentos",
      uploadCareerHistory: "Enviar histórico funcional",
      attachLeaveRecords: "Anexar afastamentos",
      updateCareerHistory: "Atualizar histórico funcional",
      downloadPdf: "Baixar PDF",
      demoDataLoaded: "Os dados abaixo já estão carregados para a demo.",
      openAccount: "Abrir conta",
      opening: "Abrindo...",
      clickUploadCareerHistory: "Clique em \"Enviar histórico funcional\" para abrir os campos de upload.",
      careerHistoryPdf: "PDF do histórico funcional",
      dateOfBirth: "Data de nascimento",
      recognizedCltYears: "Anos CLT reconhecidos",
      leaveRecordsPdf: "PDF de afastamentos",
      selectedLeaveRecordsFile: "Arquivo de afastamentos selecionado",
      fill10CltYears: "Preencher 10 anos CLT",
      upTo10CltYears: "Você pode informar até 10 anos CLT. Se já tiver esse tempo, digite 10 ou use o atalho.",
      selectedFile: "Arquivo selecionado",
      reloadLastSaved: "Recarregar último salvo",
      selectPdfToAttach: "Selecione o PDF para anexar aos dados salvos.",
      sendOtherFiles: "Para enviar outros arquivos, use os botões acima para abrir o campo correspondente.",
      pdfStorage: "Armazenamento do PDF",
      processing: "Processamento",
      timeWorked: "Tempo trabalhado",
      timeRemaining: "Tempo restante",
      events: "Eventos",
      daysAway: "Dias afastado",
      medicalReview: "Revisão médica",
      nextProgression: "Próxima progressão",
      comparison: "Comparação",
      timeWorkedAndLeave: "Tempo trabalhado e afastamento",
      noLeavePeriods: "Você não possui períodos de afastamento registrados para desenhar a comparação.",
      start: "Início",
      today: "Hoje",
      data: "Data",
      delayed: "Atrasado",
      probation: "Probatório",
      onTrack: "Em dia",
      nA: "N/A",
      medicalLeave: "Licença médica",
      medicalReviewCompleted: "Revisão médica concluída",
      daysUntilMedicalReview: "dias até a revisão médica",
      enoughEvents: "O PDF não trouxe eventos suficientes para desenhar a linha do tempo.",
      chartTitle: "Linha do tempo de progressões e promoções",
      uploadHint: "Envie o PDF do histórico funcional para analisar os dados e montar os cálculos de carreira.",
      loadedInDemo: "Aqui você verá tempo trabalhado, projeção de aposentadoria e a próxima progressão e promoção.",
      userRequiredForHistory: "Crie um usuário antes de enviar o histórico funcional.",
      userRequiredForLeave: "Crie um usuário antes de enviar afastamentos.",
      chooseCareerHistoryPdf: "Escolha um PDF do histórico funcional.",
      chooseLeaveRecordsPdf: "Escolha um PDF de afastamentos.",
      processingCareerHistory: "Processando o PDF do histórico funcional em segundo plano...",
      processingLeaveRecords: "Processando o PDF de afastamentos em segundo plano...",
      unexpectedReload: "Falha inesperada ao recarregar.",
      unexpectedAnalyze: "Falha inesperada ao analisar.",
      unexpectedAttach: "Falha inesperada ao analisar afastamentos.",
      loadSavedAnalysis: "Carregar análise salva",
      uploadFilesAbove: "Para enviar outros arquivos, use os botões acima para abrir o campo correspondente.",
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
      enterDemo: "Explore demo",
      enteringDemo: "Opening demo...",
      noAccount: "No account?",
      titleLine1: "Career",
      titleLine2: "Management",
      description:
        "Organize your professional growth with clarity, automation, and intelligence.",
    },
    authCard: {
      access: "Access",
      signIn: "Sign In",
      createAccount: "Create Account",
      loginOrEmail: "Login or Email",
      password: "Password",
      signingIn: "Signing in...",
      forgotPassword: "Forgot Password",
      resendConfirmation: "Resend Confirmation Email",
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
      emailAlreadyRegistered: "This email is already registered.",
      loginAlreadyRegistered: "This login is already registered.",
      successMessage: "Registration completed successfully. You can now sign in with your login.",
      unexpectedSave: "We could not create the account right now. Please try again.",
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
      fullName: "Full name",
      registrationNumber: "Employee ID",
      cpf: "Tax ID",
      birthDate: "Birth date",
      possessionDate: "Appointment date",
      position: "Current role",
      symbol: "Current symbol",
      level: "Level",
      grade: "Grade",
      demoHighlights: "Demo Highlights",
      viewOnly: "View Only",
      reloadLastSaved: "Reload Last Saved",
      noSession: "No active session was found. Sign in again to view your data.",
    },
    finance: {
      title: "Finance",
      subtitle:
        "Upload one or more pay stubs, then watch the batch progress as the files are processed.",
      autoImportSectionTitle: "Open the assistant to import your pay stubs",
      autoImportSectionSubtitle:
        "Sign in normally to the Portal do Servidor. Then open the pay stub page and I’ll handle the rest.",
      autoImportButton: "Open assistant now",
      autoImporting: "Opening assistant...",
      autoImportDesktopNotice: "The Windows download is still being prepared.",
      autoImportMobileNotice: "On mobile, return to a computer to use the assistant.",
      autoImportTokenLabel: "Connection code",
      autoImportExpiresLabel: "Expires at",
      autoImportHelper: "Use the manual token only if automatic launch fails.",
      assistantDownloadButton: "Download assistant",
      assistantDownloadHint: "Download the installer to open the assistant on your computer.",
      assistantInstallLink: "Download the assistant",
      mobileImportNotice:
        "You can't download the assistant from a phone. Use a computer to continue.",
      manualTokenReminderText:
        "If automatic launch does not work, generate a temporary token, paste it into the assistant window, and press Enter.",
      manualTokenModalTitle: "Temporary token",
      manualTokenModalSubtitle:
        "Copy this token and paste it into the assistant if automatic launch fails.",
      manualTokenModalHint: "Open the assistant on your computer and paste this token if needed.",
      tokenCopiedFeedback: "Token copied.",
      closeTokenModalButton: "Close",
      assistantWindowsPreparing: "Preparing the Windows download.",
      assistantStepsTitle: "How it works",
      assistantStep1: "Download the assistant",
      assistantStep2: "Open it on your computer",
      assistantStep3: "Sign in securely with gov.br",
      assistantStep4: "Your pay stubs appear here automatically",
      generateTemporaryTokenButton: "Generate temporary token",
      copyTokenButton: "Copy token",
      assistantLaunchError: "We couldn't start the import right now. Please try again.",
      assistantLaunchErrorPrefix: "We couldn't open the assistant.",
      assistantLaunchErrorSuffix: " and try again.",
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
      missingPaycheckMonthsTitle: "Missing pay stubs",
      missingPaycheckMonthsWarning:
        "There was an issue capturing the sheets for these months: {{months}}. Please upload them manually or review the analysis without those months.",
      primaryIssue: "Primary issue",
      primaryIssueNotAvailable: "Primary issue not available.",
      clearPaychecksButton: "Clear PDFs",
      clearPaychecksConfirmTitle: "Clear PDFs",
      clearPaychecksConfirmText: "Are you sure you want to delete all downloaded pay stubs?",
      clearPaychecksYes: "Yes",
      clearPaychecksNo: "No",
      clearPaychecksLoading: "Deleting...",
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
