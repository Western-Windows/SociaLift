import type * as React from "react";

declare global {
  namespace JSX {
    type Element = React.ReactElement;
    interface ElementClass extends React.Component<any> {}
    interface IntrinsicAttributes extends React.Attributes {}
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}

export {};
