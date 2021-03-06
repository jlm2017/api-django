import countries from "localized-countries/data/fr";

import validate from "@agir/lib/utils/validate";

const FIRST_COUNTRY_CODES = ["FR", "PT", "DZ", "MA", "TR", "IT", "GB", "ES"];
const FIRST_COUNTRIES = FIRST_COUNTRY_CODES.map((countryCode) => ({
  value: countryCode,
  label: countries[countryCode],
}));
const OTHER_COUNTRIES = Object.keys(countries)
  .map((countryCode) => {
    if (!FIRST_COUNTRY_CODES.includes(countryCode)) {
      return {
        value: countryCode,
        label: countries[countryCode],
      };
    }
  })
  .filter(Boolean)
  .sort(({ label: label1 }, { label: label2 }) => label1.localeCompare(label2));

export const COUNTRIES = [...FIRST_COUNTRIES, ...OTHER_COUNTRIES];

export const EVENT_DEFAULT_DURATIONS = [
  {
    value: 60,
    label: "1h",
  },
  {
    value: 90,
    label: "1h30",
  },
  {
    value: 120,
    label: "2h",
  },
  {
    value: 180,
    label: "3h",
  },
  {
    value: null,
    label: "Personnalisée",
  },
];

export const FOR_USERS_OPTIONS = [
  {
    value: "2",
    label: "La campagne présidentielle",
  },
  {
    value: "I",
    label: "Une autre campagne France insoumise",
  },
];

export const EVENT_TYPES = {
  G: {
    label: "Réunion de groupe",
    description:
      "Une réunion qui concerne principalement les membres du groupes, et non le public de façon générale. Par exemple, la réunion hebdomadaire du groupe, une réunion de travail, ou l'audition d'une association",
  },
  M: {
    label: "Événement public",
    description:
      "Un événement ouvert à tous les publics, au-delà des membres du groupe, mais qui aura lieu dans un lieu privé. Par exemple, un événement public avec un orateur, une projection ou un concert",
  },
  A: {
    label: "Action publique",
    description:
      "Une action qui se déroulera dans un lieu public et qui aura comme objectif principal  d'aller à la rencontre ou d'atteindre des personnes extérieures à la France insoumise",
  },
  O: {
    label: "Autre",
    description:
      "Tout autre type d'événement qui ne rentre pas dans les autres catégories",
  },
};

export const DEFAULT_FORM_DATA = {
  name: "",
  organizerGroup: null,
  startTime: new Date().toUTCString(),
  endTime: new Date().toUTCString(),
  subtype: null,
  forUsers: "",
  location: {
    name: "",
    address1: "",
    address2: "",
    city: "",
    zip: "",
    country: COUNTRIES[0].value,
    isDefault: true,
  },
  contact: {
    name: "",
    email: "",
    phone: "",
    hidePhone: false,
    isDefault: true,
  },
};

export const FORM_FIELD_CONSTRAINTS = {
  name: {
    presence: {
      allowEmpty: false,
      message: "Donnez un titre à votre événement",
    },
    length: {
      minimum: 3,
      maximum: 100,
      tooShort:
        "Donnez un titre à votre événement d’au moins %{count} caractères",
      tooLong:
        "Le titre de votre événement ne peut pas dépasser les %{count} caractères",
    },
  },
  organizerGroup: {
    presence: {
      allowEmpty: false,
      message: "Indiquez l'organisateur de votre événement",
    },
  },
  startTime: {
    presence: {
      allowEmpty: false,
      message: "Indiquez une date et heure de début",
    },
    datetime: {
      message: "Indiquez une date et heure valides",
    },
  },
  endTime: {
    presence: {
      allowEmpty: false,
      message: "Indiquez une date et heure de fin",
    },
    datetime: {
      message: "Indiquez une date et heure valides",
    },
  },
  forUsers: {
    presence: {
      allowEmpty: false,
      message: "Choisissez parmi les options proposées",
    },
  },
  subtype: {
    presence: {
      allowEmpty: false,
      message: "Choisissez un type parmi les options proposées",
    },
  },
  "location.name": {
    presence: {
      allowEmpty: false,
      message: "Donnez un nom au lieu où se déroule l’événement",
    },
  },
  "location.address1": {
    presence: {
      allowEmpty: false,
      message: "Indiquez l’adresse du lieu où se déroule l’évément",
    },
  },
  "location.city": {
    presence: {
      allowEmpty: false,
      message: "Indiquez la ville où se déroule l’événement",
    },
  },
  "location.zip": {
    presence: {
      allowEmpty: false,
      message: "Indiquez un code postal",
    },
  },
  "location.country": {
    presence: {
      allowEmpty: false,
      message: "Indiquez le nom du pays où se déroule l’événement",
    },
  },
  "contact.name": {
    presence: {
      allowEmpty: false,
      message:
        "Indiquez le nom de la personne à contacter concernant cet événement",
    },
  },
  "contact.email": {
    presence: {
      allowEmpty: false,
      message:
        "Indiquez une adresse e-mail de contact pour les personnes qui souhaiteraient se renseigner",
    },
    email: {
      message: "Indiquez une adresse e-mail valide",
    },
  },
  "contact.phone": {
    presence: {
      allowEmpty: false,
      message: "Indiquez un numéro de téléphone",
    },
    phone: {
      message: "Indiquez un numéro de téléphone valide",
    },
  },
};

export const validateData = (data) =>
  validate(data, FORM_FIELD_CONSTRAINTS, {
    format: "cleanMessage",
    fullMessages: false,
  });
