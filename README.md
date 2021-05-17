# MCAC-Job-Sceduling-Problem

## 專案簡介
該專案為台大資管所學生廖梓妘、龔汶佑及黃楷翔在研究 job scheduling problem 時，同時應考慮維修排程影響的產能損失及良率損失而面臨的最佳化問題。在研究中，我們首先透過數學模型試圖取得最佳解，並進一步設計演算法以在可接受的時間內找到接近最佳解的可能解。過程中研究了兩種不同的目標式、多種演算法設定以及多種 uniform distribution random 產生的 20 筆實驗資料，並實驗效果。

## 資料內容
- experiments：內含所有實驗程式，包含原目標式(最小化 completion time)、新目標式(最小化 tardiness weighted cost) 以及數學模型。
- result_summary：為實驗結果
- MCAC_final：最終研究短論文

## 實驗資料設計
- 第一行(實驗設定): 機台數 / 訂單數 / 最多修幾台 / 最晚time period(也可以不寫)
- Machine: 產能 / 下降速率 / 維修時間 / 初始良率 / 最低良率
- job: 訂單量 / 完成日期 / 訂單權重