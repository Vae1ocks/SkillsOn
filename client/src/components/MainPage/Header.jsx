import styles from "./Header.module.scss";
import logo from "../../assets/skillson_logo.svg";
import searchIcon from "../../assets/Vectorsearch_icon.svg";
import chatIcon from "../../assets/chat_icon.svg";
import accountIcon from "../../assets/avatar_icon.svg";

function NavButton({ children }) {
  return <button className={styles.navButton}>{children}</button>;
}

function Search() {
  return (
    <form className={styles.search}>
      <div className={styles.border}>
        <input className={styles.searchBar} placeholder="Что хотите изучить?" />
      </div>
      <button className={styles.searchButton} type="submit" alt="поиск">
        <img src={searchIcon} />
      </button>
    </form>
  );
}

function Header({ isLoggedIn = false }) {
  return (
    <header className={styles.header}>
      <NavButton>
        <img src={logo}></img>
      </NavButton>
      <nav className={styles.nav}>
        {!isLoggedIn ? (
          <NavButton>Каталог курсов</NavButton>
        ) : (
          <>
            <NavButton>Каталог курсов</NavButton>
            <NavButton>Мои курсы</NavButton>
          </>
        )}
      </nav>
      <Search />
      <div className={styles.auth}>
        {!isLoggedIn ? (
          <>
            <NavButton>Bход</NavButton>
            <NavButton>Регистрация</NavButton>
          </>
        ) : (
          <>
            <NavButton>
              <img src={chatIcon} />
            </NavButton>
            <NavButton>
              <img src={accountIcon} />
            </NavButton>
          </>
        )}
      </div>
    </header>
  );
}

export default Header;
