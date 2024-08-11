import styles from "./Consultation.module.scss";
import bgForm from "../../assets/bg_dec_form.svg";
import fgForm from "../../assets/form.png";

function Consultation() {
  return (
    <div className={styles.consultation}>
      <div className={styles.banner}>
        <img className={styles.bg} src={bgForm} />
        <img src={fgForm} />
        <p className={styles.title}>Остались вопросы?</p>
        <p className={styles.desc}>
          Наши консультанты помогут во всем разобраться
        </p>
      </div>
      <form>
        <div className={styles.input}>
          <input placeholder="Имя" />
          <input placeholder="+7 (999) 999-99-99" />
        </div>
        <div className={styles.submit}>
          <button type="submit">Получить консультацию</button>
          <input name="checkbox" type="checkbox" />
          <label htmlFor="checkbox">
            Нажимая на кнопку, я даю согласие на обработку персональных данных
          </label>
        </div>
      </form>
    </div>
  );
}

export default Consultation;
