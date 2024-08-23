import styles from "./Info.module.scss";
import bgInstructors from "../../assets/bg_dec_advantages_teacher.svg";
import fgInstructors from "../../assets/advantages_instructors.png";
import fgCommunication from "../../assets/advantages_communication.png";
import bgCourses from "../../assets/bg_wide_range.svg";
import bgExperience from "../../assets/bg_experience.svg";

function InfoCard({ wide = false, blue = false, title, desc, fg, bg }) {
  return (
    <div
      className={wide ? `${styles.infoCard} ${styles.wide}` : styles.infoCard}
      style={blue ? { background: "#2871ee" } : {}}
    >
      <p style={blue ? { color: "#f5f5f5" } : {}} className={styles.title}>
        {title}
      </p>
      <p style={blue ? { color: "#f5f5f5" } : {}}>{desc}</p>
      {bg && <img className={styles.bg} src={bg} />}
      {fg && <img className={styles.fg} src={fg} />}
    </div>
  );
}

function Info() {
  return (
    <div className={styles.info}>
      <p className={styles.title}>Обучение в удовольствие</p>
      <div className={styles.row1}>
        <InfoCard
          wide={true}
          title="Проверенные преподаватели"
          desc="Наш сервис предлагает вам возможность выбирать только проверенных
        преподавателей благодаря наличию отзывов и рейтингов."
          fg={fgInstructors}
          bg={bgInstructors}
        />
        <InfoCard
          wide={true}
          blue={true}
          title="Возможность связаться с преподавателем"
          desc="Одним из главных преимуществ нашего сервиса является возможность узнать у преподавателя о курсе. Вы можете задать все интересующие вас вопросы, уточнить детали курса или узнать дополнительные условия."
          fg={fgCommunication}
        />
      </div>
      <div className={styles.row2}>
        <InfoCard
          title="Рекомендации согласно предпочтениям"
          desc="Наш сервис анализирует ваши интересы и предпочтения, чтобы предложить вам наиболее подходящие курсы."
        />
        <InfoCard
          blue={true}
          title="Большой спектр курсов, в том числе бесплатных"
          desc="Мы предлагаем широкий выбор курсов по различным направлениям, включая как платные, так и бесплатные варианты. Независимо от вашего уровня знаний и бюджета, вы всегда найдете что-то полезное и интересное."
          bg={bgCourses}
        />
        <InfoCard
          title="Возможность поделиться личным опытом"
          desc="После прохождения курса вы можете оставить свой отзыв, поделиться своими впечатлениями и оценить качество обучения"
          bg={bgExperience}
        />
      </div>
    </div>
  );
}

export default Info;
