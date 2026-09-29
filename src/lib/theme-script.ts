export const THEME_KEY = "heaprace:theme";

/**
 * Runs in <head> before the page paints, so a saved dark theme never flashes light first.
 * Light is the default (LeetCode-style); dark only when the visitor picked it.
 */
export const themeInitScript = `try{if(localStorage.getItem("${THEME_KEY}")==="dark")document.documentElement.dataset.theme="dark"}catch(e){}`;
