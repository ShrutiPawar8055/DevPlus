interface HeaderProps {
  onHome: () => void;
}

export default function Header({ onHome }: HeaderProps) {
  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="logo" onClick={onHome} style={{ cursor: "pointer" }}>
          <div className="logo-mark">L</div>
          <h1>LLD Practice</h1>
        </div>
        <span style={{ color: "var(--green-light)", fontSize: "0.9rem" }}>
          Learn. Design. Iterate.
        </span>
      </div>
    </header>
  );
}
