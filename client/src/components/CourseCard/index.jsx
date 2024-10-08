import styles from "./CourseCard.module.scss";
import ratingIcon from "../../assets/rating_icon.svg";
import reviewIcon from "../../assets/review_icon.svg";

function CourseCard({
  wide = false,
  level,
  title,
  author,
  rating,
  reviews,
  price,
}) {
  let reviewsText;
  switch (reviews % 10) {
    case 1:
      reviewsText = "отзыв";
      break;
    case 2:
      reviewsText = "отзыва";
      break;
    case 3:
      reviewsText = "отзыва";
      break;
    case 4:
      reviewsText = "отзыва";
      break;
    default:
      reviewsText = "отзывов";
  }
  return (
    <div className={wide ? `${styles.card} ${styles.wide}` : styles.card}>
      <p
        className={`${styles.level} ${
          level == "Junior"
            ? styles.junior
            : level == "Middle"
            ? styles.middle
            : styles.senior
        }`}
      >
        {level}
      </p>
      <div className={styles.infoContainer}>
        <button className={styles.position}>{title}</button>
        <p className={styles.author}>
          Автор: <span>{author}</span>
        </p>
      </div>
      <div className={styles.statsContainer}>
        <div className={styles.rating}>
          <img src={ratingIcon} />
          <p>{rating}</p>
        </div>
        <button className={styles.reviews}>
          <img src={reviewIcon} />
          <p>
            {reviews} {reviewsText}
          </p>
        </button>
      </div>
      <div className={styles.purchase}>
        <p>{price}₽</p>
        <button>Купить</button>
      </div>
    </div>
  );
}

export default CourseCard;
