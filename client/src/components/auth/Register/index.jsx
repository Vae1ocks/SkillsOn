import React from 'react';
import { Link } from 'react-router-dom';
import './Register.css';

const Registration = () => {
    return (
        <>
          <div className="logo"><Link to="/main"/></div>
  <div className="back-link">
  <Link to="/login">Назад</Link></div>
        <div className="registration-container">
            <div className="registration-form">
                <h1>Регистрация</h1>
                <div className="step-indicator">
                    <span className="active-step">1</span>
                    <span>2</span>
                    <span>3</span>
                </div>
                <form>
                    <div className='input-group'>
                    <input type="text" placeholder="Имя" required />
                    <input type="text" placeholder="Фамилия" required />
                    </div>
                    <input type="email" placeholder="Email" required />
                    <input type="password" placeholder="Пароль" required />
                    <input type="password" placeholder="Подтверждение пароля" required />
                    <div className="in-row">
                    <button type="submit">Зарегистрироваться</button>
                    <div className="agreement">
                    <input type="checkbox" required />
                    <span className='text-checkbox'>Нажимая на кнопку, я даю согласие на обработку персональных данных</span>
                </div>
                </div>
                </form>
                <div className="login-link">
                    Уже есть аккаунт? <Link to="/login">Войти</Link>
                </div>
            </div>
            <div className="spinner"/>
            <div className="arrow" />
        </div>
</>
    );
};

export default Registration;
