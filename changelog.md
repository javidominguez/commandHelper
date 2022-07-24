* The category jump gesture is now generated using scanCode, thus it is independent of the keyboard language. This way it should work on keyboards with non-latin alphabets.
* Fixed: The windows and alt keys are prevented from being pressed when the virtual menu is active. This prevents inadvertent focus changes. Previously getScript was not able to intercept these keys.


