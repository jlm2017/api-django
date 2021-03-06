import PropTypes from "prop-types";
import React from "react";
import { animated, useSpring } from "react-spring";
import styled from "styled-components";
import SwiperCore, { A11y } from "swiper";
import { Swiper, SwiperSlide } from "swiper/react";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import GroupSuggestionCard from "./GroupSuggestionCard";

SwiperCore.use([A11y]);

export const Carousel = styled(animated.div)``;
export const Block = styled(animated.div)``;
export const StyledWrapper = styled.div`
  padding-top: 48px;
  padding-bottom: 56px;
  text-align: center;

  @media (max-width: ${style.collapse}px) {
    text-align: left;
    padding-top: 0;
    padding-bottom: 0;
  }

  & > * {
    margin-left: 1.5rem;
  }

  h4 {
    margin-bottom: 1rem;
    font-size: 1.25rem;
    line-height: 1.5;
    font-weight: 700;

    @media (max-width: ${style.collapse}px) {
      font-size: 1rem;
      font-weight: 600;
    }
  }

  ${Button} {
    margin-bottom: 1.5rem;
  }

  ${Carousel} {
    @media (max-width: ${style.collapse}px) {
      margin-left: 0;
    }
    .swiper-container {
      @media (max-width: ${style.collapse}px) {
        padding-left: 1.5rem;
      }
      .swiper-slide {
        width: auto;
      }
    }
  }

  ${Block} {
    display: flex;
    flex-flow: row nowrap;
    justify-content: center;

    @media (max-width: ${style.collapse}px) {
      justify-content: flex-start;
    }

    & > * {
      flex: 1 1 397px;

      @media (min-width: ${style.collapse}px) {
        margin-right: 2rem;
      }
    }
  }
`;

export const GroupSuggestionCarousel = (props) => {
  const { groups } = props;
  const style = useSpring({
    from: {
      opacity: 0,
      paddingLeft: 24,
    },
    to: {
      opacity: 1,
      paddingLeft: 0,
    },
  });

  if (groups.length === 0) {
    return null;
  }

  return (
    <Carousel style={style}>
      <Swiper spaceBetween={16} slidesPerView="auto">
        {groups.map((group) => (
          <SwiperSlide key={group.id}>
            <GroupSuggestionCard {...group} />
          </SwiperSlide>
        ))}
      </Swiper>
    </Carousel>
  );
};

export const GroupSuggestionBlock = (props) => {
  const { groups } = props;
  const style = useSpring({
    from: {
      opacity: 0,
      paddingLeft: 24,
    },
    to: {
      opacity: 1,
      paddingLeft: 0,
    },
  });

  if (groups.length === 0) {
    return null;
  }

  return (
    <Block style={style}>
      {groups.map((group) => (
        <GroupSuggestionCard {...group} key={group.id} />
      ))}
    </Block>
  );
};

export const GroupSuggestions = (props) => {
  const { groups } = props;

  return (
    <PageFadeIn ready={Array.isArray(groups) && groups.length > 0}>
      <StyledWrapper>
        <h4>Autres groupes qui peuvent vous intéresser</h4>
        <Button as="Link" route="groupMapPage" icon="map" small>
          Carte des groupes
        </Button>
        <ResponsiveLayout
          MobileLayout={GroupSuggestionCarousel}
          DesktopLayout={GroupSuggestionBlock}
          {...props}
        />
      </StyledWrapper>
    </PageFadeIn>
  );
};

GroupSuggestionCarousel.propTypes = GroupSuggestionBlock.propTypes = GroupSuggestions.propTypes = {
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    })
  ),
};

export default GroupSuggestions;
