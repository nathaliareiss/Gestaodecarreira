import Link from "next/link"

export function UsuarioHeroSection() {
  return (
    <div className="hero-copy hero-copy--register">
      <div className="hero-topbar">
        <p className="eyebrow">Cadastro de usuario</p>
        <Link className="ghost-button ghost-button--compact" href="/login">
          Ja tenho conta
        </Link>
      </div>

      <h1>Career Progression Analyzer</h1>
    
      <p className="hero-text">
       Cadastre-se para assumir o controle da sua carreira de forma prática. Fique tranquilo: seus dados estarão seguros e ninguém terá acesso a eles.
       Register now to take practical control of your career. Rest assured: your data will remain secure and inaccessible to others.
      </p>
    </div>
  )
}
