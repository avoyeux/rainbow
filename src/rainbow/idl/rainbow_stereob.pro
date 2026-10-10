function linear, x
	return, x
end

start_date = '23-jul-2012 00:00'
end_date = '25-jul-2012 11:59'
;end_date = '25-jul-2012 23:59'

wave = '304'

instr = 'euvib'

scaling = 'linear'

outpath = 'C:\Users\Frédéric Auchère\Documents\01 - Projects\01 - Science\Oscillations\Rainbow\helio_' + wave + '\'

const_init

redo = 0

lonwidth = 45.0
latwidth = 45.0
loncen = 195.0
latcen =  0.0d
merlonmax = 65.0

dlon = 0.075
dlat = 0.075

npx = round(lonwidth/dlon)
npy = round(latwidth/dlat)

delim = get_delim()

if redo eq 1 then begin

	if instr eq 'euvia' then space = 'a' else space = 'b'
	list_scc = scc_read_summary(date=[start_date, end_date], tele='euvi', space=space,$
		                   source='lz',type='img', errmsg=errmsg, /nobeacon, /check, /debris)
	good = where(list_scc.value eq wave, count)

	if count lt 2 then stop

	list_scc = list_scc[good]

	list_dates = anytim2utc(list_scc.date_obs)

	path = scc_data_path(space, date=[start_date, end_date], tele='euvi', source='lz', type='img')
	list_files = path + delim + strmid(list_scc.filename, 0, 8) + delim + list_scc.filename

	n = n_elements(list_files)

	orbitdeb = get_stereo_lonlat(start_date, space, system='Carrington', /degrees)
	orbitfin = get_stereo_lonlat(end_date, space, system='Carrington', /degrees)

	londeb = (orbitdeb[1] + 360.0) mod 360.0
	latdeb = orbitdeb[2]
	lonfin = (orbitfin[1] + 360.0) mod 360.0
	latfin = orbitfin[2]
	orbits = replicate({lon:0.0, lat:0.0, dist:0.0}, n)
	dum = get_stereo_lonlat(list_dates, space, system='Carrington', /degrees)
	dates = list_dates.mjd + list_dates.time/86400000.0d
	orbits.dist = reform(dum[0, *])
	orbits.lon = reform(dum[1, *])
	orbits.lat = reform(dum[2, *])

	lon_fit = poly_fit(dates-dates[0], (orbits.lon+360.0-orbits[0].lon) mod 360.001, 2, /double)      ;decimal to avoid wrap around at exactly 360.0
	lat_fit = poly_fit(dates-dates[0], orbits.lat-orbits[0].lat, 2, /double)
	dist_fit = poly_fit(dates-dates[0], orbits.dist-orbits[0].dist, 2, /double)
	lon_fit[0] = lon_fit[0] - lon_fit[1]*dates[0] + orbits[0].lon + lon_fit[2]*dates[0]^2.0
	lat_fit[0] = lat_fit[0] - lat_fit[1]*dates[0] + orbits[0].lat + lat_fit[2]*dates[0]^2.0
	lon_fit[1] = lon_fit[1] - 2.0*lon_fit[2]*dates[0]
	lat_fit[1] = lat_fit[1] - 2.0*lat_fit[2]*dates[0]
	dist_fit[0] = dist_fit[0] - dist_fit[1]*dates[0] + orbits[0].dist + dist_fit[2]*dates[0]^2.0
	dist_fit[1] = dist_fit[1] - 2.0*dist_fit[2]*dates[0]

	mid_date = (dates[0] + dates[n-1])/2.0

	helio = fltarr(npx, npy, n)

	datainfo_template = {datainfo, strdate:'', cdelt1:0.0, cdelt2:0.0, crpix1:0.0, crpix2:0.0, nx:0.0, ny:0.0, roll:0.0, solar_r:0.0, date:0.0d, lon:0.0, lat:0.0, dist:0.0, wavelnth:'', quality:0, exptime:0.0}

	datainfos = replicate(datainfo_template, n)

	for in=0L, n-1 do begin

		print, in, n

		datainfo = datainfo_template
		secchi_prep, list_files[in], subhdr, subimg, /use_smask, /nocalfac_butcorrforipsum
		subimg = despike_gen(subimg, tn=8, /low3)
		datainfo.wavelnth = strtrim(subhdr.wavelnth, 2)
		datainfo.crpix1 = subhdr.crpix1-1
		datainfo.crpix2 = subhdr.crpix2-1
		datainfo.nx = subhdr.naxis1
		datainfo.ny = subhdr.naxis2
		datainfo.roll = -subhdr.crota
		datainfo.date = list_dates[in].mjd + list_dates[in].time/86400000.0d
		datainfo.strdate = list_scc[in].date_obs

		datainfo.lon = float(lon_fit[0] + (lon_fit[1] + lon_fit[2]*datainfo.date)*datainfo.date)
		datainfo.lat = float(lat_fit[0] + (lat_fit[1] + lat_fit[2]*datainfo.date)*datainfo.date)
		dist = float(dist_fit[0] + (dist_fit[1] + dist_fit[2]*datainfo.date)*datainfo.date)

		datainfo.solar_r = !radeg*atan(!const_ro/dist/1d3)/(subhdr.cdelt1/3600.0)
		datainfo.dist = dist

		mask = data2hel(subimg gt 0, datainfo, npx, npy, $
			loncen-lonwidth/2.0d, loncen+lonwidth/2.0d, latcen-latwidth/2.0d, latcen+latwidth/2.0d, $
			-90.0, 90.0, cos(merlonmax*!dtor), missing=1, ref_date=mid_date)

		helio[*, *, in] = mask*data2hel(subimg>0, datainfo, npx, npy, $
			loncen-lonwidth/2.0d, loncen+lonwidth/2.0d, latcen-latwidth/2.0d, latcen+latwidth/2.0d, $
		 	-90.0, 90.0, cos(merlonmax*!dtor), missing=-1, cubic=-0.5, /c2limb, ref_date=mid_date)

		datainfos[in] = datainfo

	endfor

	save, filename=outpath + 'rainbow_stereob_' + wave + '.save', helio, npx, npy, n, datainfos, latwidth, lonwidth, latcen, loncen, dlon, dlat, mid_date

endif else begin

	restore, outpath + 'rainbow_stereob_' + wave + '.save'

endelse

	avg = rebin(helio, npx, npy, 1)
	medi = median(helio, dimension=3)
	;helio = smooth(helio, [1, 1, 1], /edge_truncate) - smooth(helio, [1, 1, 20], /edge_truncate)
	;helio = helio - smooth(helio, [1, 1, 3], /edge_truncate)
	;helio = helio - (shift(helio, 0, 0, 1) + shift(helio, 0, 0, -1))/2.0
  ;helio = smooth(helio, [1, 1, 5], /edge_truncate)
  ;helio = helio - rebin(avg, npx, npy, n)
  ;helio = helio - rebin(medi, npx, npy, n)

	avg = rebin(helio, npx, npy, 1)

	window, xs=npx, ys=npy

	cube = bytarr(3, npx, npy)
	byt = auto_bytscl(call_function(scaling, avg), mini=scl_mini, maxi=scl_maxi, minval=0.01, maxval=0.99)

	;scl_mini = -300; alog10(100.)
	;scl_maxi = 300 ; alog10(1500.0)
	if scaling eq 'linear' then begin
	  scl_mini = 0.25; alog10(100.)
	  scl_maxi = 1.75 ; alog10(1500.0)
  endif else begin
    scl_mini = alog10(100.)
    scl_maxi = alog10(1500.0)
  endelse

	frames = helio

	for in=0, n-1 do begin

	  	if scaling eq 'linear' then $
	  	  frames[*, *, in] = helio[*, *, in] / median(helio[*, *, (in-20)>0:(in+20)<(n-1)], dimension=3) $
	  	else $
	  	  frames[*, *, in] = helio[*, *, in]

  endfor

  for in=0, n-1 do begin

    byt = bytscl(call_function(scaling, rebin(frames[*, *, (in-1)>0:(in+1)<(n-1)], 600, 600, 1)), min=scl_mini, max = scl_maxi)
    ;byt = bytscl(call_function(scaling, frames[*, *, in]), min=scl_mini, max = scl_maxi)
		cube[0, *, *] = byt
		cube[1, *, *] = byt
		cube[2, *, *] = byt

		 strid = strtrim(string(in, format='(I5)'), 2)
		 if in lt 10 then strid = '0' + strid
		 if in lt 100 then strid = '0' + strid
		 if in lt 1000 then strid = '0' + strid

		 tv, cube, true=1

		 frame = tvrd(true=1)
		 strdate = utc2str(str2utc(datainfos[in].strdate))
		 while strpos(strdate, ':') ne -1 do begin
		 	strput, strdate, '-', strpos(strdate, ':')
		 endwhile
		 write_png, outpath + delim + strid + '_' + strdate + '.png', frame

	endfor

	avifile = outpath + 'rainbow_stereob_' + wave + '.mp4'
	spawnline = 'ffmpeg -framerate 25 -i "' + outpath + '%4d.png"' + ' -vcodec libx264 -pix_fmt yuv420p -preset slow -crf 17 -y "' + avifile + '"'
	spawn, spawnline

	listpng = file_search(outpath + '*.png')
	;file_delete, listpng, /allow_nonexistent

end