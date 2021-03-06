import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import { useHistory } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { routeConfig } from "@agir/front/app/routes.config";

import { displayIntervalStart } from "@agir/lib/utils/time";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import {
  Column,
  Hide,
  Row,
  useResponsiveMemo,
} from "@agir/front/genericComponents/grid";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";
import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";
import Map from "@agir/carte/common/Map";
import Spacer from "@agir/front/genericComponents/Spacer";

import eventCardDefaultBackground from "@agir/front/genericComponents/images/event-card-default-bg.svg";

const RSVPButton = ({ id, hasSubscriptionForm, rsvped, routes, schedule }) => {
  if (schedule.isBefore(DateTime.local())) {
    return null;
  }

  if (rsvped) {
    return (
      <Button
        as="Link"
        small
        color="confirmed"
        icon="check"
        to={
          routeConfig.eventDetails
            ? routeConfig.eventDetails.getLink({ eventPk: id })
            : routes.details
        }
      >
        Je participe
      </Button>
    );
  }

  if (hasSubscriptionForm) {
    return (
      <Button small as="a" href={routes.rsvp}>
        Participer
      </Button>
    );
  }

  return (
    <CSRFProtectedForm
      method="post"
      action={routes.rsvp}
      style={{ display: "inline-block" }}
    >
      <Button small type="submit" icon="calendar">
        Participer
      </Button>
    </CSRFProtectedForm>
  );
};

RSVPButton.propTypes = {
  id: PropTypes.string,
  hasSubscriptionForm: PropTypes.bool,
  rsvped: PropTypes.bool,
  routes: PropTypes.shape({
    details: PropTypes.string,
    rsvp: PropTypes.string,
  }),
  schedule: PropTypes.instanceOf(Interval),
};

const Buttons = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  line-height: 3.125rem;
  margin-top: -0.5rem;

  ${Button} {
    margin-top: 0.5rem;
  }
`;
const Illustration = styled.div`
  background-color: ${({ $img }) => ($img ? "#e5e5e5" : "#fafafa")};
  display: grid;
  z-index: 0;
  width: 100%;
  max-width: 270px;

  @media (max-width: ${style.collapse}px) {
    margin: -1rem -1rem 1rem;
    width: calc(100% + 2rem);
    max-width: 100vw;
  }

  & > * {
    grid-column: 1/2;
    grid-row: 1/2;
    z-index: 1;
    max-height: inherit;
    max-width: 100%;
  }

  &::before {
    content: "";
    z-index: 0;
    grid-column: 1/2;
    grid-row: 1/2;
    display: ${({ $img }) => ($img ? "block" : "none")};
    height: 100%;
    width: 100%;
    background-image: url(${({ $img }) => $img});
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center center;
    opacity: 0.25;
  }

  img {
    max-height: 200px;
    margin: 0 auto;
    align-self: center;
  }
`;

const StyledCard = styled(Card)`
  width: 100%;

  && header {
    margin-bottom: 1.25rem;
  }

  ${Row} {
    font-size: 0.875rem;
    max-width: calc(100% - 2rem);
  }

  ${Column} {
    max-width: 100%;
  }

  @media only screen and (min-width: ${style.collapse}px) {
    display: grid;
    grid-template-columns: 270px 1fr;
    grid-template-rows: auto auto;
    grid-gap: 1.5rem;
    padding: 0;

    ${Illustration} {
      grid-row: span 2;
      margin: 0;
    }

    header,
    ${Row} {
      margin: 0;
      padding: 0;
      padding-right: 1.5rem;
    }

    header {
      padding-top: 1.5rem;
    }

    ${Row} {
      padding-bottom: 1.5rem;
      max-width: auto;

      ${Column} {
        padding: 0;
      }
    }
  }
`;

const EventCardIllustration = (props) => {
  const { image, coordinates, subtype } = props;

  const isVisible = useResponsiveMemo(!!image, true);

  if (!isVisible) {
    return null;
  }

  if (image) {
    return (
      <Illustration $img={image}>
        <img src={image} alt="Image d'illustration" />
      </Illustration>
    );
  }
  if (Array.isArray(coordinates)) {
    return (
      <Illustration>
        <Map
          zoom={11}
          center={coordinates}
          iconConfiguration={subtype}
          isStatic
        />
      </Illustration>
    );
  }
  return (
    <Illustration>
      <img
        src={eventCardDefaultBackground}
        alt="Image d'illustration par défaut"
      />
    </Illustration>
  );
};
EventCardIllustration.propTypes = {
  image: PropTypes.string,
  coordinates: PropTypes.array,
  subtype: PropTypes.object,
};

const EventCard = (props) => {
  const {
    id,
    illustration,
    hasSubscriptionForm,
    schedule,
    location,
    subtype,
    name,
    participantCount,
    rsvp,
    routes,
    groups,
    compteRendu,
  } = props;
  const history = useHistory();
  const handleClick = React.useCallback(
    (e) => {
      if (["A", "BUTTON"].includes(e.target.tagName.toUpperCase())) {
        return;
      }
      id &&
        routeConfig.eventDetails &&
        history.push(routeConfig.eventDetails.getLink({ eventPk: id }));
    },
    [history, id]
  );

  return (
    <StyledCard onClick={handleClick}>
      <EventCardIllustration
        image={illustration}
        subtype={subtype}
        coordinates={
          location && location.coordinates && location.coordinates.coordinates
        }
      />
      <header>
        <p
          style={{
            fontSize: "14px",
            color: schedule.isBefore(DateTime.local())
              ? style.black500
              : style.primary500,
            fontWeight: 500,
          }}
        >
          {displayIntervalStart(schedule)}
          {location && location.shortLocation && (
            <> • {location.shortLocation}</>
          )}
        </p>
        <h3
          style={{
            fontWeight: 700,
            fontSize: "1rem",
            marginTop: 0,
            marginBottom: "0.4rem",
          }}
        >
          {name}
        </h3>
        {Array.isArray(groups) && groups.length > 0
          ? groups.map((group) => (
              <p
                key={group.name}
                style={{
                  fontWeight: "400",
                  fontSize: "14px",
                  lineHeight: "1",
                  color: style.black1000,
                }}
              >
                &mdash;&nbsp;{group.name}
              </p>
            ))
          : null}
      </header>
      <Row>
        <Column grow collapse={0}>
          <Buttons>
            <Button
              small
              color="primary"
              as="Link"
              to={
                routeConfig.eventDetails
                  ? routeConfig.eventDetails.getLink({ eventPk: id })
                  : routes.details
              }
            >
              Voir l'événement
              <RawFeatherIcon
                name="arrow-right"
                width="1rem"
                height="1rem"
                style={{ marginLeft: "0.5rem" }}
              />
            </Button>
            <Spacer size=".5rem" />
            <RSVPButton
              id={id}
              hasSubscriptionForm={hasSubscriptionForm}
              rsvped={rsvp === "CO"}
              routes={routes}
              schedule={schedule}
            />
            {compteRendu ? (
              <>
                <Spacer size=".5rem" />
                <Button
                  small
                  color="tertiary"
                  icon="file-text"
                  as="Link"
                  to={
                    routeConfig.eventDetails
                      ? routeConfig.eventDetails.getLink({ eventPk: id })
                      : routes.details
                  }
                >
                  Voir le compte-rendu
                </Button>
              </>
            ) : null}
          </Buttons>
        </Column>
        {participantCount > 1 && (
          <Column
            collapse={0}
            style={{ paddingTop: "0.5rem", alignSelf: "flex-end" }}
          >
            {participantCount}{" "}
            <Hide as="span" under={400}>
              participant⋅es
            </Hide>
            <Hide as="span" over={401}>
              <FeatherIcon inline small name="user" />
            </Hide>
          </Column>
        )}
      </Row>
    </StyledCard>
  );
};

EventCard.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  participantCount: PropTypes.number,
  hasSubscriptionForm: PropTypes.bool,
  illustration: PropTypes.string,
  schedule: PropTypes.instanceOf(Interval).isRequired,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortLocation: PropTypes.string,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }),
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.shape({
    details: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    compteRendu: PropTypes.string,
  }),
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
    })
  ),
  compteRendu: PropTypes.string,
  subtype: PropTypes.object,
};

export default EventCard;
