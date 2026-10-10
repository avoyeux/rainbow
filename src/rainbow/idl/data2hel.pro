
function data2hel, img, datainfo, theta_size, phi_size, lonmin, lonmax, latmin, latmax, merlonmin, merlonmax, tresh, bilin=bilin, $
         cubic=cubic, missing=missing, c2limb=c2limb, ref_date=ref_date

  ;datainfo = {datainfo, crpix1:0.0, crpix2:0.0d, nx:0.0, ny:0.0, roll:0.0, solar_r:0.0, date:0.0, lon:0.0, lat:0.0, wavelnth:''}
  ;date & ref_date in julian days, ie using anytim2utc
  ;crpix1 & 2 with bottom left pixel = 0,0, lon, lat, roll in degrees
  ;c2limb = center to limb correction


  waves = ['171', '195', '284', '304']
  ap = [14.18, 14.56d, 14.50d, 14.60d, 14.51d]
  bp = [0.0, -2.65d, -2.14d, -0.71d, -3.12d]
  cp = [0.0, 0.96d,   0.66d, -1.18d,  0.34d]
  dr = [1.0, 1.005, 1.005, 1.005, 1.01]
  iwave = 1 + (where(waves eq datainfo.wavelnth))[0]

  sc_roll = !dtor*datainfo.roll

  lon = 2.0*!pi - !dtor*datainfo.lon
  lat = !dtor*datainfo.lat

  linlat = !dtor*(latmin + (latmax - latmin)*findgen(phi_size)/phi_size)
  latitude = replicate(1.0, theta_size) # linlat
  longitude = ((!dtor*(lonmin + (lonmax - lonmin)*findgen(theta_size)/theta_size) + lon)  mod (2.0*!pi)) # replicate(1.0, phi_size)

  if keyword_set(ref_date) then begin

    dlon = -!dtor*(datainfo.date - ref_date)*(ap[iwave] + bp[iwave]*sin(linlat)^2.0 + cp[iwave]*sin(linlat)^4.0 - 14.18)

    longitude = temporary(longitude) - (replicate(1.0, theta_size) # dlon)

  endif

  good = where((longitude gt (2.0*!dpi+!dpi*(merlonmin>(-180.0d))/180.0d)) or (longitude lt (!pi*(merlonmax<180.0d)/180.0d)), count)

  if keyword_set(missing) then hel = replicate(float(missing), theta_size, phi_size) else hel = fltarr(theta_size, phi_size)

  if count gt 0 then begin

    p1x = 0.0
    p1y = 0.0

    xc = datainfo.crpix1
    yc = datainfo.crpix2
    rc = datainfo.solar_r*dr[iwave]

    x = cos(latitude[good])*sin(longitude[good])
    y = sin(latitude[good])
    z = cos(latitude[good])*cos(longitude[good])
    dummy = (z*cos(lat) + y*sin(lat))
    y = y*cos(lat) - z*sin(lat)

    g = where(dummy ge tresh, count)
    if count gt 0 then begin

      x = x[g]
      y = y[g]

      z = x*sin(sc_roll) + y*cos(sc_roll)
      x = x*cos(sc_roll) - y*sin(sc_roll)
      y = z

      if keyword_set(c2limb) and (datainfo.wavelnth ne '304') then begin
        a = 0.1
        theta = asin(sqrt(x^2.0d + y^2.0d))
        mu = -cos(theta)/a + sqrt(1.0 + 2.0/a + (cos(theta)/a)^2.0)
      endif else mu = 1.0

      x = rc*x + xc - p1x
      y = rc*y + yc - p1y

      if (keyword_set(bilin) or keyword_set(cubic)) then $
        hel[good[g]] = interpolate(img, x, y, cubic=cubic, missing=missing)/mu $
      else hel[good[g]] = img[round(x), round(y)]/mu

    endif

  endif

  return, hel

end
