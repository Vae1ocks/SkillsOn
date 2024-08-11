import styles from "./CourseTypeCard.module.scss";
import type0 from "../../assets/type0.png";
import type1 from "../../assets/type1.png";
import type2 from "../../assets/type2.png";
import type3 from "../../assets/type3.png";

function CourseTypeCard({ imgSrc }) {
  let img;
  switch (imgSrc) {
    case 0:
      img = type0;
      break;
    case 1:
      img = type1;
      break;
    case 2:
      img = type2;
      break;
    case 3:
      img = type3;
      break;
    default:
      throw Error("image doesn't exist");
  }
  return (
    <button className={styles.card}>
      <img src={img} />
    </button>
  );
}

export default CourseTypeCard;
