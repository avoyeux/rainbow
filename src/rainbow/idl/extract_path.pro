function extract_path, img, degree=degree

        if ~keyword_set(degree) then degree = 6

        poly_template = {poly, xmin:0.0, xmax:0.0, coeffs:ptr_new()}

        sz = size(img)

        x = indgen(sz[1]) # replicate(1, sz[2])
        y = replicate(1, sz[1]) # indgen(sz[2])

        path = where(img eq 0, count)

        if count gt 0 then begin

                x = x[path]
                y = y[path]
                srt = sort(x)
                x = x[srt]
                y = y[srt]

                res = poly_fit(x, y, degree, /double)

                return, {poly, xmin:min(x), xmax:max(x), coeffs:ptr_new(res)}

        endif else return, -1

end

