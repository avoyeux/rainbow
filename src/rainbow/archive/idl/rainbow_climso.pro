function linear, x
	return, x
end

const_init

start_date = '23-jul-2012 00:00'
end_date = '25-jul-2012 11:59'

instr = 'c1'

scaling = 'alog10'

inpath = 'C:\archive\CLIMSO\'
outpath = 'C:\Users\Frédéric Auchère\Documents\01 - Projects\01 - Science\Oscillations\Rainbow\CLIMSO\'

redo = 0

theta_min = 245.0
theta_max = 295.0
rho_min = 936.0
rho_max = 1180.0 ;arcseonds

npx = 1250.0
npy = 400.0

delim = get_delim()

if redo eq 1 then begin

	list_files = file_search(inpath + instr + delim, '*b1.fts')

	n = n_elements(list_files)

	polar = fltarr(npx, npy, n)
	strdates = strarr(n)
	lindates = dblarr(n)

	for in=0L, n-1 do begin

		print, in, n

		subimg = readfits(list_files[in], subhdr)

		dist = (get_sun(fxpar(subhdr, 'DATE_OBS')))[0]*!const_astronomical_unit
		subhdr = fitshead2struct(subhdr, /silent)

		strdates[in] = subhdr.date_obs
		dum = anytim2utc(strdates[in])
		lindates[in] = dum.mjd + dum.time/86400000.0d

		crpix1 = 1100.0
		crpix2 = 1070.0
	 	cdelt1 = 1.2
	 	cdelt2 = 1.2

		polar[*, *, in] = polar_map(subimg, npx, npy, crpix1, crpix2, theta_min - subhdr.solar_p0*!radeg, theta_max - subhdr.solar_p0*!radeg, rho_min/cdelt1, rho_max/cdelt2, /bilin)

	endfor

	save, file=outpath + 'rainbow_climso_' + instr + '.save', polar, instr, strdates, lindates, n

endif else begin

	restore, outpath + 'rainbow_climso_' + instr + '.save'

	;avg = rebin(helio, npx, npy, 1)
	;helio = helio - smooth(helio, [1, 1, 20], /edge_truncate)
	;helio = helio - rebin(avg, npx, npy, n)

	avg = rebin(polar, npx, npy, 1)

	window, xs=npx, ys=npy

	cube = bytarr(3, npx, npy)
	byt = auto_bytscl(call_function(scaling, avg), mini=scl_mini, maxi=scl_maxi, minval=0.01, maxval=0.97)

	;scl_mini = -300; alog10(100.)
	;scl_maxi = 300 ; alog10(1500.0)
	;scl_mini = alog10(100.)
;	scl_maxi = alog10(1500.0)

	for in=0, n-1 do begin

		byt = bytscl(call_function(scaling, polar[*, *, in]), min=scl_mini, max = scl_maxi)
		cube[0, *, *] = byt
		cube[1, *, *] = byt
		cube[2, *, *] = byt

		 strid = strtrim(string(in, format='(I5)'), 2)
		 if in lt 10 then strid = '0' + strid
		 if in lt 100 then strid = '0' + strid
		 if in lt 1000 then strid = '0' + strid

		tv, cube, true=1

		 frame = tvrd(true=1)
		 write_png, outpath + delim + strid + '.png', frame

	endfor

	avifile = outpath + 'rainbow_climso_' + instr + '.mp4'
	spawnline = 'ffmpeg -framerate 25 -i "' + outpath + '%4d.png"' + ' -vcodec libx264 -pix_fmt yuv420p -preset slow -crf 17 -y "' + avifile + '"'
	spawn, spawnline

	listpng = file_search(outpath + '*.png')
	file_delete, listpng, /allow_nonexistent


endelse

end
