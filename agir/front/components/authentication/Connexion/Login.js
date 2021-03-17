import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import arrowRight from "@agir/front/genericComponents/images/arrow-right.svg";
import chevronDown from "@agir/front/genericComponents/images/chevron-down.svg";
import style from "@agir/front/genericComponents/_variables.scss";
import LoginMailEmpty from "./LoginMailEmpty";
import LoginFacebook from "./LoginFacebook";
import styled from "styled-components";
import Link from "@agir/front/app/Link";
import { BlockSwitchLink } from "@agir/front/authentication/Connexion/styledComponents";
import { login } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory } from "react-router-dom";
import { useBookmarkedEmails } from "@agir/front/authentication/hooks";

const Toast = styled.div`
  padding: 1rem;
  border: 1px solid #000a2c;
  position: relative;
  margin-top: 2rem;

  div {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 6px;
    background-color: #e93a55;
  }
`;

const ShowMore = styled.div`
  font-weight: 700;
  color: ${style.primary500};
  margin-top: 21px;
  cursor: pointer;
  display: inline-block;
  text-align: left;
`;

const ContainerConnexion = styled.div`
  width: 400px;
  max-width: 100%;
`;

const LoginMailButton = styled(Button)`
  margin-top: 0.5rem;
  margin-left: 0;
  max-width: 100%;
  width: 400px;
  justify-content: space-between;
`;

const ToastNotConnected = () => {
  return (
    <Toast>
      <div></div>
      Vous devez vous connecter pour accéder à cette page
    </Toast>
  );
};

//const mockMails = ["nom.prenom@email.com", "test@franceinsoumise.org"];

const Login = () => {
  const history = useHistory();
  const bookmarkedEmails = useBookmarkedEmails();
  const [showMore, setShowMore] = useState(false);

  const handleShowMore = () => {
    setShowMore(true);
  };

  const loginBookmarkedMail = async (email) => {
    const data = await login(email);
    console.log("data", data);
    const route = routeConfig.codeLogin.getLink();
    history.push(route);
  };

  return (
    <ContainerConnexion>
      <h1>Je me connecte</h1>

      <BlockSwitchLink>
        <span>Pas encore de compte ?</span>
        &nbsp;
        <span>
          <Link route="signup">Je m'inscris</Link>
        </span>
      </BlockSwitchLink>

      {/* <ToastNotConnected /> */}

      {bookmarkedEmails[0].length > 0 && (
        <div style={{ marginTop: "24px" }}>
          <span style={{ fontWeight: 500 }}>À mon compte :</span>

          {bookmarkedEmails[0].map((mail, id) => (
            <LoginMailButton
              key={id}
              color="primary"
              onClick={() => loginBookmarkedMail(mail)}
            >
              {mail}
              <img src={arrowRight} style={{ color: "white" }} />
            </LoginMailButton>
          ))}
        </div>
      )}

      {!showMore ? (
        <ShowMore onClick={handleShowMore}>
          Afficher tout <img src={chevronDown} alt="Afficher plus" />
        </ShowMore>
      ) : (
        <div
          style={{ textAlign: "center", marginTop: "20px", fontSize: "14px" }}
        >
          OU
        </div>
      )}

      {(showMore || !(bookmarkedEmails[0].length > 0)) && <LoginMailEmpty />}

      <div style={{ textAlign: "center", margin: "20px", fontSize: "14px" }}>
        OU
      </div>
      <LoginFacebook />
    </ContainerConnexion>
  );
};

export default Login;