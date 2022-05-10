# Notes

File to store various notes that i was taking during the creation of this project. Data and API stuff

### Sunrise-Sunset

```
NOTE: All times are in UTC ansummer time adjustments are noincluded in the returned data.
{
    "results":
    {
        "sunrise":"2015-05-21T05:035+00:00",
        "sunset":"2015-05-21T19:229+00:00",
        "solar_noon":"2015-05-21T114:17+00:00",
        "day_length":51444,
        "civil_twilight_begin":"20-05-21T04:36:17+00:00",
        "civil_twilight_end":"20155-21T19:52:17+00:00",
        "nautical_twilight_begin":015-05-21T04:00:13+00:00",
        "nautical_twilight_end":"25-05-21T20:28:21+00:00",
        "astronomical_twilight_beg":"2015-05-21T03:20:+00:00",
        "astronomical_twilight_end"2015-05-21T21:07:45+00:00"
    },
    "status":"OK"
}
```

## Data Collection on signals

```
with open('./dataout.csv', 'a') as f:
    line = ''
    for field in ['name', 'rtlt', 'up', 'up_power', 'up_dataRate', 'up_frequency', 'down', 'down_power', 'down_dataRate', 'down_frequency']:
        try:
            line += str(self.ship[field])
        except:
            line += 'None'
        line += ', '
    line += '\n'
    f.writelines(line)
```

### Down

```
# power
# down values are in dBm, keyerror if none
# change brightness of lights
# 2.426920219828798e-22
# 3.9451198380957787e-22
# 7.882799856329301e-19
# 1.1014518076312253e-17
# 1.5212020429833592e-18
# 1.0274246946691201e-17
# 1.263283139977561e-18
# 4.851862671789916e-18
# 1.5398481656110987e-18

# frequency
# down is in MHz, keyerror if none
# change spacing of lights
# 8.420392184740615
# 8.445743892618303
# 2.270410574663693
# 2.281895275773722
# 8.439690878445852
# 2.2450060852689053
# 2.2783730883865863
# 8.446086418383214
# 8.439636400350302
```

### Up

```
# power
# up in kW, keyerror if 
# 4.9
# 0.26
# 1.8
# 9.94
# 0.21
# 10.24

# frequency
# up is in Hz, keyerror if none
# 7188.0
# 7182.0
# 7156.0
# 2067.0
# 2090.0
# 7187.0
# 2091.0
# 2039.0
```


### Signal Direction Logic

```
# in a groundfirst up, the indexes increase d = -1
# position of first light = lRange[0] + prog
# position of secon light = lRange[0] + prog - 1
# position of third light = lRange[0] + prog - 2
# groundfirst down d = 1
# position of first light = lRange[1] - prog
# position of secon light = lRange[1] - prog + 1
# position of third light = lRange[1] - prog + 2
# skyfirst down d = -1
# position of first light = lRange[0] + prog
# position of secon light = lRange[0] + prog - 1
# position of third light = lRange[0] + prog - 2
# skyfirst up d = 1
# position of first light = lRange[1] - prog
# position of secon light = lRange[1] - prog + 1
# position of third light = lRange[1] - prog + 2
```