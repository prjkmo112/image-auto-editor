declare module '*.module.scss' {
    const classes: { readonly [key: string]: string };
    export default classes;
}

declare var process: any;