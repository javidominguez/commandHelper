# commandHelper

此 NVDA 附加元件提供了另一種執行指令的方法，好讓那些不方便按複雜按鍵的人也能執行特定操作。

### 使用方法

按 NVDA+H 來開啟指令協助員，然後可以使用下列鍵盤操作：

* 左右方向鍵選擇指令類型。
* 上下方向鍵可從當前類型中選擇想要執行的指令。
* 按 Enter 鍵來執行目前選擇的指令。
* 按 Shift+Enter 會以「連按兩下」的方式來執行目前選擇的指令。
* 按 Control+Enter 會以「連按三下」的方式執行目前選擇的指令。 
* 英文字母 A 到 Z 可跳到以該字母為開頭的類型。
* 按 F1 唸出目前選擇之指令的對應手勢。
* 按 Esc 鍵即可離開指令協助模式，並回到平時的鍵盤操作。

### 設定

你可以從 NVDA 的「偏好 > 輸入手勢」來指定用哪個按鍵來啟動指令協助員。

其他按鍵則可以透過 NVDA 的「偏好 > 設定 > 指令協助員」來設定。

* 啟用或停用 control 鍵來啟動指令管理員。
* 選擇用來結束協助員的按鍵。
* 選擇用來報讀指令操作手勢的按鍵。 
* 透過數字鍵盤來啟用或停用協助員。

#### 使用 control 鍵來啟動協助員

有些人不方便按複雜的按鍵組合，此時只要勾選此項，即可連續按五次 control 鍵來啟動協助員。然而，此方法可能會因為有時需要按 control 鍵來執行其他操作而意外啟動了協助員，例如使用 control+C 和 control+V 來複製和貼上。要避免這種情況，你可以透過 Windows 控制台的鍵盤設定來降低按鍵的重複速度。此附加元件的偏好設定對話窗裡面有一個按鈕可直接開啟鍵盤設定視窗，或者你也可以在 Windows 開始功能表中輸入「鍵盤」，然後按 Enter 來開啟鍵盤設定視窗。在設定鍵盤時，你必須把「重複速度」盡量設得小一點；若設定為 0，雖然可避免意外啟動指令協助員，但其缺點是無法透過持續按住 control 鍵的方式來啟動協助員，而這正好是那些不方便連續快速按鍵的人所偏好的操作方式。因此，每個人應該要根據自己的需求或偏好來選擇合適的設定。

#### 數字鍵盤

當你勾選此項，便可使用數字鍵盤的按鍵來操作指令協助員。

* 數字鍵 4 和 6 可用來選擇指令類型。
* 數字鍵 2 和 8 可以從當前的指令類型中選擇某個指令。
* 數字鍵 5 可以報讀目前選擇的指令所對應的操作手勢。
* 按 Enter 鍵來執行指令。
* 加號會以「連按兩下」的方式來執行目前選擇的指令。
* 減號會以「連按三下」的方式執行目前選擇的指令。 
* Del 鍵可離開指令協助模式，並回到平常的鍵盤輸入模式。

關於相容性：此附加元件可相容於先前版本的 NVDA。目前所測試過的最早版本是 NVDA 2018.1，比這更早的版本應該也能執行。不過，萬一指令協助員在舊版 NVDA 當中執行時出現問題，開發者也不會提供相關的技術支援。