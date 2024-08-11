import styles from "./Banner.module.scss";
import bannerDec from "../../assets/bg_dec_baner.svg";
import bannerImg from "../../assets/baner.png";

function Banner() {
  return (
    <div className={styles.banner}>
      <img className={styles.dec} src={bannerDec} />
      <img className={styles.img} src={bannerImg} />
      <div>
        <p className={styles.title}>Поможем быстро прокачать новую профессию</p>
        <p>Уже через месяц сможешь сделать свой первый проект</p>
      </div>
    </div>
  );
}

export default Banner;
