import { useState } from "react";
import { Link } from "react-router-dom";
import "./LoginPage.css";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authResult, setAuthResult] = useState(null);
  const [show, setShow] = useState(false);

  return (
    <div className="login">
      <div className="logo">
        <Link to="/main" />
      </div>
      <div className="back-link">
        <Link to="/login">Назад</Link>
      </div>

      <div className="login-form">
        <h1>Добро пожаловать!</h1>
        <form>
          <input
            type="email"
            placeholder="Email"
            required
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Пароль"
            required
            onChange={(e) => {
              setPassword(e.target.value);
            }}
            className="second-input"
          />
          <button type="submit">Войти</button>
        </form>
        <div className="register-link">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </div>
        <div className="forgot-password-link">
          <a href="#">Забыли пароль</a>
        </div>
      </div>
      <div className="spinner" />
      <div className="arrow" />
    </div>
  );
};

export default LoginPage;
