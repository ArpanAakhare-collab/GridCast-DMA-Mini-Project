# GridCast — Viva Questions and Answers

1. **What is GridCast?**  
   GridCast is a DMA mini-project that analyzes electricity-consumption time series and compares short-term forecasting methods.

2. **What is time-series data?**  
   Data recorded in chronological order at regular or meaningful time intervals.

3. **What is a trend?**  
   The long-term direction of a series, such as increasing, decreasing or relatively stable consumption.

4. **What is seasonality?**  
   A pattern that repeats at a fixed interval. GridCast checks for a weekly pattern using a period of seven days.

5. **What is residual or noise?**  
   The part left after trend and seasonal components are removed; it contains irregular variation and model error.

6. **Why use a moving average?**  
   It smooths short-term fluctuations so the underlying trend is easier to see. A 7-day window summarizes one week of daily observations.

7. **What is ARIMA?**  
   AutoRegressive Integrated Moving Average. It combines lagged observations (AR), differencing (I) and lagged forecast errors (MA).

8. **What do p, d and q mean?**  
   p is the autoregressive order, d is the number of differencing operations, and q is the moving-average error order.

9. **Why can differencing be needed?**  
   Differencing helps remove changing levels or trend so a series can be closer to stationary.

10. **What is stationarity?**  
    A time series is stationary when key statistical properties, such as mean and variance, do not change systematically over time.

11. **What is MAE?**  
    Mean Absolute Error: the average absolute difference between actual and predicted values. Lower values are better on the same scale.

12. **What is RMSE?**  
    Root Mean Squared Error: the square root of mean squared prediction errors. It penalizes large errors more strongly than MAE.

13. **Why not randomly shuffle a time series?**  
    Random splitting can leak future information into training. Chronological splitting better represents the task of forecasting future observations.

14. **Why compare against a baseline?**  
    A complex model is useful only if it performs meaningfully against simple methods such as the last value or a moving average.

15. **Why use a separate test period?**  
    It estimates performance on observations not used to fit the model and helps avoid reporting training performance as forecast accuracy.

16. **How is daily kWh estimated from the UCI data?**  
    The `Global_active_power` field is a minute-averaged power value in kW. GridCast takes the mean valid value for each day and multiplies it by 24 hours. It is an estimate and assumes valid readings represent the full day.

17. **How are missing values handled?**  
    Days with less than 90% of the expected 1,440 minute readings are marked missing; missing daily values are interpolated using time and edge filling. This processing must be acknowledged as a limitation.

18. **Why is the best model selected by RMSE?**  
    RMSE emphasizes larger errors. The project selects the lowest RMSE on its defined holdout, but MAE is also reported and different criteria may choose differently.

19. **Does the best model guarantee future accuracy?**  
    No. Results depend on the dataset, time window and changing patterns. The holdout is only an estimate of future performance.

20. **What are the dataset's limitations?**  
    It represents one household in France during 2006–2010; it is not representative of current Indian households, a city or the national grid. It also contains missing measurement values.

21. **What is the purpose of the dashboard?**  
    It makes statistics, trends, seasonality, model errors and forecasts easier to explore without reading raw output files.

22. **What could be improved in future?**  
    Add weather, holidays, tariff, occupancy and multiple-meter data; compare SARIMA or other forecasting methods; and use rolling-origin evaluation.
