#!/usr/bin/env Rscript
# ===========================================================================
# xlsx2pzfx.R  —  panel xlsx  →  GraphPad Prism XML (.pzfx) 데이터 테이블 생성기
#
# (Python 판 xlsx2pzfx.py 와 동일 동작의 R 이식본. exe 컴파일/서명이 필요 없어
#  관리되는 Windows 에서도 R 만 설치돼 있으면 바로 실행 가능.)
#
# 실행 방법
#   1) 원클릭(더블클릭용): 인자 없이 실행하면 파일 선택 창이 뜸
#         Rscript xlsx2pzfx.R
#      (run_pzfx.bat 를 더블클릭하면 이 방식으로 실행됨)
#   2) 명령줄:
#         Rscript xlsx2pzfx.R "입력.xlsx" ["출력.pzfx"]
#
# 필요 패키지: readxl  (없으면 자동 설치 시도)
# ===========================================================================

# ---- 패키지 준비 -----------------------------------------------------------
# 관리자 권한이 필요한 시스템 라이브러리(C:/Program Files/R/.../library) 대신,
# 쓰기 가능한 '개인 라이브러리'에 설치한다 (권한 문제 회피).
ensure_pkg <- function(pkg) {
  if (requireNamespace(pkg, quietly = TRUE)) return(invisible(TRUE))

  userlib <- strsplit(Sys.getenv("R_LIBS_USER"), .Platform$path.sep)[[1]][1]
  if (is.na(userlib) || userlib == "") {
    userlib <- file.path(
      path.expand("~"), "R", paste0(R.version$os, "-library"),
      paste(R.version$major, strsplit(R.version$minor, "\\.")[[1]][1], sep = ".")
    )
  }
  dir.create(userlib, recursive = TRUE, showWarnings = FALSE)
  .libPaths(c(userlib, .libPaths()))

  message(sprintf("패키지 '%s' 를 개인 라이브러리에 설치합니다:\n  %s", pkg, userlib))
  tryCatch(
    install.packages(pkg, lib = userlib, repos = "https://cloud.r-project.org"),
    error = function(e) message("설치 중 오류: ", conditionMessage(e))
  )

  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf(paste0(
      "패키지 '%s' 설치에 실패했습니다.\n",
      "  - 인터넷이 막혀 있거나 회사 프록시 때문일 수 있습니다.\n",
      "  - 해결: RStudio 를 열고 아래를 한 번 실행하세요 (관리자 권한 불필요):\n",
      "        install.packages(\"%s\")\n",
      "    'Would you like to use a personal library?' 물으면 Yes 를 누르세요.\n",
      "    설치 후 이 스크립트를 다시 실행하면 됩니다."
    ), pkg, pkg))
  }
  invisible(TRUE)
}
ensure_pkg("readxl")
suppressWarnings(suppressMessages(library(readxl)))

# ---- 설정 ------------------------------------------------------------------
GROUP_TITLES  <- c("Chow diet", "Western diet", "TRF", "ADF", "RC")
GROUP_COUNT   <- 5L
PANEL_LABELS  <- c("(Absolute Count)" = "abs", "(Percentage)" = "pct", "(MFI)" = "MFI")
PANEL_TITLE   <- c(abs = "absolute count", pct = "Percentage", MFI = "MFI")
PANEL_ORDER   <- c("abs", "pct", "MFI")
PANEL_DECIMALS <- c(abs = 2L, pct = 3L, MFI = 0L)
PANEL_SCALE   <- c(abs = 1, pct = 100, MFI = 1)   # Percentage 는 비율(0~1) → 퍼센트(0~100)
PREFERRED_SHEET <- "Prism_Master_Ordered"

# ---- 유틸 ------------------------------------------------------------------
pick_sheet <- function(path, preferred = PREFERRED_SHEET) {
  sh <- excel_sheets(path)
  if (!is.null(preferred) && preferred %in% sh) return(preferred)
  pr <- sh[grepl("^Prism_", sh)]
  if (length(pr) == 1) return(pr[1])
  if (length(sh) == 1) return(sh[1])
  if (length(pr) >= 1) return(pr[1])
  stop(sprintf("데이터 시트를 특정할 수 없습니다. 있는 시트: %s", paste(sh, collapse = ", ")))
}

# 시트를 문자 행렬로 읽기 (숫자/텍스트 혼재 → 전부 text 로 읽고 숫자는 나중에 변환)
read_matrix <- function(path, sheet) {
  df <- suppressMessages(read_excel(
    path, sheet = sheet, col_names = FALSE,
    col_types = "text", .name_repair = "minimal"
  ))
  m <- as.matrix(df)
  dimnames(m) <- NULL
  m
}

cell <- function(m, r, c) {
  if (r >= 1 && r <= nrow(m) && c >= 1 && c <= ncol(m)) m[r, c] else NA_character_
}

as_num <- function(x) suppressWarnings(as.numeric(x))

# 셀 파싱: 값 뒤에 '*' 가 붙어 있으면 (예: "12.3*") Prism excluded value 로 표시
parse_cell <- function(x) {
  if (is.na(x)) return(list(value = NA_real_, excluded = FALSE))
  s <- trimws(x)
  excluded <- grepl("\\*\\s*$", s)
  if (excluded) s <- trimws(sub("\\*+\\s*$", "", s))
  list(value = as_num(s), excluded = excluded)
}

xml_escape <- function(s) {
  s <- gsub("&", "&amp;", s, fixed = TRUE)
  s <- gsub("<", "&lt;", s, fixed = TRUE)
  s <- gsub(">", "&gt;", s, fixed = TRUE)
  s
}

# 부동소수점 잡음 제거 후 최단 표현
fmt_num <- function(v) {
  v <- round(v, 10)
  if (v == round(v)) return(format(v, scientific = FALSE, trim = TRUE))
  format(v, digits = 15, nsmall = 0, scientific = FALSE, trim = TRUE)
}

# ---- 파싱 ------------------------------------------------------------------
# 반환: list of block; block = list(name=, panels=list(pkey=grid))
#       grid = list of rows; row = list(vals=numeric(5), excl=logical(5))
#       (NA=빈칸, excl=TRUE 면 excluded value)  ※ 위치 보존
parse_blocks <- function(m) {
  nrows <- nrow(m)

  # 그룹 행 감지: "Chow.diet"(점) / "Chow diet"(공백) 등 표기 차이 허용
  norm_key <- function(x) tolower(gsub("[[:space:].]+", "", trimws(x)))
  is_grouprow <- function(r) {
    v <- cell(m, r, 1)
    !is.na(v) && norm_key(v) == "chowdiet"
  }

  panel_cols_at <- function(r) {
    found <- integer(0)
    ncol_r <- ncol(m)
    for (c in seq_len(ncol_r)) {
      v <- cell(m, r, c)
      if (!is.na(v)) {
        key <- PANEL_LABELS[trimws(v)]
        if (!is.na(key)) found[[key]] <- c
      }
    }
    if ("abs" %in% names(found)) found else NULL
  }

  # POPNAME 행 + 패널 열 + 그룹 행 찾기
  metas <- list()
  for (r in seq_len(nrows)) {
    c0 <- cell(m, r, 1)
    if (is.na(c0) || trimws(c0) == "") next
    c0t <- trimws(c0)
    if (norm_key(c0t) == "chowdiet" || startsWith(c0t, "(")) next
    panel_cols <- NULL; panel_r <- NA
    for (rr in (r + 1):(r + 2)) {
      pc <- panel_cols_at(rr)
      if (!is.null(pc)) { panel_cols <- pc; panel_r <- rr; break }
    }
    if (is.null(panel_cols)) next
    grp_r <- NA
    for (rr in (panel_r + 1):(panel_r + 2)) {
      if (is_grouprow(rr)) { grp_r <- rr; break }
    }
    if (is.na(grp_r)) next
    metas[[length(metas) + 1]] <- list(pop_r = r, name = c0t,
                                       panel_cols = panel_cols, grp_r = grp_r)
  }

  blocks <- list()
  for (i in seq_along(metas)) {
    md <- metas[[i]]
    data_start <- md$grp_r + 1
    data_end <- if (i < length(metas)) metas[[i + 1]]$pop_r - 1 else nrows

    panels <- list()
    for (pkey in names(md$panel_cols)) {
      c0 <- md$panel_cols[[pkey]]
      scale <- PANEL_SCALE[[pkey]]
      grid <- list()
      if (data_start <= data_end) {
        for (r in data_start:data_end) {
          vals <- rep(NA_real_, GROUP_COUNT)
          excl <- rep(FALSE, GROUP_COUNT)
          for (g in seq_len(GROUP_COUNT)) {
            pc <- parse_cell(cell(m, r, c0 + g - 1))
            if (!is.na(pc$value)) {
              vals[g] <- pc$value * scale
              excl[g] <- pc$excluded
            }
          }
          grid[[length(grid) + 1]] <- list(vals = vals, excl = excl)
        }
      }
      # 아래쪽 완전 빈 행 제거 (내부 빈칸은 위치 보존)
      while (length(grid) > 0 && all(is.na(grid[[length(grid)]]$vals))) {
        grid[[length(grid)]] <- NULL
      }
      if (length(grid) > 0) panels[[pkey]] <- grid
    }
    blocks[[length(blocks) + 1]] <- list(name = md$name, panels = panels)
  }
  blocks
}

# g번째 그룹 열의 값/제외 플래그 (빈칸 제외, 위치 정렬 유지)
col_values <- function(grid, g) {
  vals <- vapply(grid, function(row) row$vals[g], numeric(1))
  excl <- vapply(grid, function(row) row$excl[g], logical(1))
  keep <- !is.na(vals)
  list(vals = vals[keep], excl = excl[keep])
}

# ---- .pzfx 생성 ------------------------------------------------------------
build_pzfx <- function(blocks) {
  tables <- list(); skipped <- character(0)
  for (blk in blocks) {
    if (length(blk$panels) == 0) { skipped <- c(skipped, blk$name); next }
    for (pkey in PANEL_ORDER) {
      if (!is.null(blk$panels[[pkey]])) {
        tables[[length(tables) + 1]] <- list(
          title = paste(blk$name, PANEL_TITLE[[pkey]]),
          grid = blk$panels[[pkey]],
          decimals = PANEL_DECIMALS[[pkey]]
        )
      }
    }
  }

  o <- c()
  o <- c(o, '<?xml version="1.0" encoding="UTF-8"?>')
  o <- c(o, '<GraphPadPrismFile xmlns="http://graphpad.com/prism/Prism.htm" PrismXMLVersion="5.00">')
  o <- c(o, "<Created>")
  o <- c(o, '<OriginalVersion CreatedByProgram="xlsx2pzfx.R" CreatedByVersion="1.0" Login="" DateTime="0000-00-00T00:00:00"/>')
  o <- c(o, "</Created>")
  o <- c(o, "<InfoSequence>", '<Ref ID="Info0" Selected="1"/>', "</InfoSequence>")
  o <- c(o, '<Info ID="Info0">', "<Title>Project info</Title>", "<Notes></Notes>",
         '<Constant><Name>Experiment Date</Name><Value></Value></Constant>',
         '<Constant><Name>Experiment ID</Name><Value></Value></Constant>', "</Info>")
  o <- c(o, "<TableSequence>")
  for (i in seq_along(tables)) {
    sel <- if (i == 1) ' Selected="1"' else ""
    o <- c(o, sprintf('<Ref ID="Table%d"%s/>', i - 1, sel))
  }
  o <- c(o, "</TableSequence>")
  for (i in seq_along(tables)) {
    tb <- tables[[i]]
    o <- c(o, sprintf('<Table ID="Table%d" XFormat="none" YFormat="replicates" Replicates="1" TableType="OneWay" EVFormat="AsteriskAfterNumber">', i - 1))
    o <- c(o, sprintf("<Title>%s</Title>", xml_escape(tb$title)))
    for (g in seq_len(GROUP_COUNT)) {
      cv <- col_values(tb$grid, g)
      o <- c(o, sprintf('<YColumn Width="81" Decimals="%d" Subcolumns="1">', tb$decimals))
      o <- c(o, sprintf("<Title>%s</Title>", xml_escape(GROUP_TITLES[g])))
      o <- c(o, "<Subcolumn>")
      if (length(cv$vals) > 0) {
        o <- c(o, vapply(seq_along(cv$vals), function(k) {
          if (cv$excl[k]) sprintf('<d Excluded="1">%s*</d>', fmt_num(cv$vals[k]))
          else            sprintf("<d>%s</d>", fmt_num(cv$vals[k]))
        }, character(1)))
      }
      o <- c(o, "</Subcolumn>", "</YColumn>")
    }
    o <- c(o, "</Table>")
  }
  o <- c(o, "</GraphPadPrismFile>")
  list(xml = paste(o, collapse = "\n"), tables = tables, skipped = skipped)
}

convert_file <- function(xlsx_path, out_path = NULL, sheet = NULL) {
  if (is.null(out_path)) out_path <- sub("\\.[^.]*$", ".pzfx", xlsx_path)
  sheet_name <- if (is.null(sheet)) pick_sheet(xlsx_path) else sheet
  message(sprintf("  시트: %s", sheet_name))
  m <- read_matrix(xlsx_path, sheet_name)
  blocks <- parse_blocks(m)
  res <- build_pzfx(blocks)
  writeLines(enc2utf8(res$xml), con = out_path, useBytes = TRUE)
  list(out = out_path, tables = res$tables, skipped = res$skipped, blocks = blocks)
}

summary_text <- function(r) {
  lines <- c(sprintf("생성 완료: %s", r$out), "", sprintf("테이블 %d개:", length(r$tables)))
  for (i in seq_along(r$tables)) {
    tb <- r$tables[[i]]
    cvs <- lapply(seq_len(GROUP_COUNT), function(g) col_values(tb$grid, g))
    ns <- vapply(cvs, function(cv) length(cv$vals), integer(1))
    nex <- sum(vapply(cvs, function(cv) sum(cv$excl), integer(1)))
    ex_note <- if (nex > 0) sprintf("  [제외 %d개]", nex) else ""
    lines <- c(lines, sprintf("  [%2d] %s  (n=%s)%s", i - 1, tb$title, paste(ns, collapse = ","), ex_note))
  }
  if (length(r$skipped) > 0) lines <- c(lines, "", paste("건너뛴 블록(데이터 없음):", paste(r$skipped, collapse = ", ")))
  lines <- c(lines, "", "다음 단계: Prism에서 이 .pzfx 열기 → 그래프 세팅 → .prism 으로 저장")
  paste(lines, collapse = "\n")
}

# ---- 진입점 ----------------------------------------------------------------
main <- function() {
  args <- commandArgs(trailingOnly = TRUE)

  if (length(args) == 0) {
    # 원클릭(더블클릭): 파일 선택 창
    xlsx <- tryCatch(file.choose(), error = function(e) "")
    if (is.null(xlsx) || xlsx == "") { message("취소됨."); return(invisible()) }
    r <- convert_file(xlsx)
    msg <- summary_text(r)
    # 완료 알림: Windows 면 팝업, 아니면 콘솔
    shown <- FALSE
    if (.Platform$OS.type == "windows" && requireNamespace("utils", quietly = TRUE)) {
      shown <- tryCatch({ utils::winDialog("ok", msg); TRUE }, error = function(e) FALSE)
    }
    if (!shown && requireNamespace("tcltk", quietly = TRUE)) {
      shown <- tryCatch({ tcltk::tkmessageBox(title = "완료", message = msg); TRUE },
                        error = function(e) FALSE)
    }
    cat(msg, "\n")
  } else {
    xlsx <- args[1]
    out <- if (length(args) >= 2) args[2] else NULL
    if (!file.exists(xlsx)) stop(sprintf("입력 xlsx 없음: %s", xlsx))
    message(sprintf("■ xlsx 파싱: %s", xlsx))
    r <- convert_file(xlsx, out)
    cat(summary_text(r), "\n")
  }
}

main()
