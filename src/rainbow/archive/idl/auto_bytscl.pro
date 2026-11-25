function auto_bytscl, img, MINI = mini, MAXI = maxi, MINVAL=minval, MAXVAL = maxval

	IF~KEYWORD_SET(MINVAL) THEN minval = 0.01
	IF~KEYWORD_SET(MAXVAL) THEN maxval = 0.99

	sz = SIZE(img)
	nx = 128>(sz[1]/8.0)<1024
	ny = 128>(sz[2]/8.0)<1024
	im = CONGRID(img, nx, ny)
	x2 = ((FINDGEN(nx)/nx - 0.5)^2.0) # REPLICATE(1.0, ny)
	y2 = REPLICATE(1.0, nx) # ((FINDGEN(ny)/ny - 0.5)^2.0)
	r2 = x2 + y2
	valid = WHERE(FINITE(im) EQ 1, count)

    IF count GT 0 THEN BEGIN

		im = im[valid]

		pos = WHERE(im GT 0, poscount)
		neg = WHERE(im LT 0, negcount)
		IF poscount GT 0 THEN im[pos] = SQRT(im[pos])
		IF negcount GT 0 THEN im[neg] = -SQRT(-im[neg])

		minim = MIN(im, MAX = maxim)
    	histo = HISTOGRAM(im, MIN = minim, MAX = maxim, NBINS=2000, LOCATIONS = x)
    	histo = MEDIAN(histo, 3)

		tot = TOTAL(ABS(histo*x), /DOUBLE, /CUMULATIVE)
		tot = tot/tot[N_ELEMENTS(tot)-1]

 		good = WHERE((tot GE minval) AND (tot LE maxval), count)
    	IF count GT 0 THEN BEGIN
    		mini = MIN(x[good], MAX = maxi)
    		IF mini GT 0 THEN mini = mini^2.0 ELSE mini = -mini^2.0
    		IF maxi GT 0 THEN maxi = maxi^2.0 ELSE maxi = -maxi^2.0
    	ENDIF ELSE mini = MIN(im, MAX = maxi)

		IF mini EQ maxi THEN mini = MIN(im, MAX = maxi)

    ENDIF ELSE BEGIN

    	maxi = 255.0
    	mini = 0.0

    ENDELSE

	return, byte((255*((img - mini)>0)/(maxi - mini))<255)

END
