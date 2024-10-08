import styles from "./ReviewCard.module.scss";
import dropdownIcon from "../../assets/icon_dropdown.svg";
import defaultAvatar from "../../assets/avatar.png";

function Star({ active }) {
  return (
    <svg
      width="25"
      height="24"
      viewBox="0 0 25 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12.3333 3.9021L14.8053 8.9101L20.3333 9.7181L16.3333 13.6141L17.2773 19.1181L12.3333 16.5181L7.38934 19.1181L8.33334 13.6141L4.33334 9.7181L9.86134 8.9101L12.3333 3.9021Z"
        fill={active ? "#6F97FF" : "#cccccc"}
        stroke={active ? "#6F97FF" : "#cccccc"}
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ReviewCard({ avatar = defaultAvatar, name, course, rating, review }) {
  return (
    <div className={styles.reviewCard}>
      <div className={styles.generalInfo}>
        <img src={avatar} />
        <div>
          <p className={styles.name}>{name}</p>
          <p className={styles.course}>
            Курс: <button>{course}</button>
          </p>
        </div>
      </div>
      <div className={styles.rating}>
        {Array.from(Array(5).keys()).map((idx) => (
          <Star key={idx} active={idx < rating} />
        ))}
      </div>
      <p className={styles.review}>
        {review.length > 217 ? `${review.slice(0, 217)}...` : review}
      </p>
      {review.length > 217 && (
        <button className={styles.showMore}>
          Показать полностью
          <img src={dropdownIcon} />
        </button>
      )}
    </div>
  );
}

export default ReviewCard;
