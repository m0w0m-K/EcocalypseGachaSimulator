import random
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from multiprocessing import Pool
import math

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def gacha_n_times(arg):
    ceil = arg[1]  # 픽업 천장 초기화
    weight = arg[2]  # 가중치 초기화
    ssr_count = 0  # SSR 뽑기 개수
    pickup_count = 0  # 픽업 뽑기 개수
    
    for _ in range(1, arg[0]+1, 1):
        # 가중치에 따른 SSR 확률 증가
        if weight < 30:
            ssr_probability = 151  # 가중치가 30 미만일 때, SSR 확률 0.01% 증가
        elif weight < 40:
            ssr_probability = 180  # 가중치가 30 이상 40 미만일 때, SSR 확률 0.3% 증가
        elif weight < 50:
            ssr_probability = 250  # 가중치가 40 이상 50 미만일 때, SSR 확률 1% 증가
        elif weight == 50:
            ssr_probability = 10000  # 가중치가 50일 때, SSR 확률 100% (무조건 SSR)

        # SSR 뽑기 시도
        if random.random() * 10000 < ssr_probability:
            ssr_count += 1
            ssr_probability = 150  # SSR 확률 초기화
            weight = 0  # 가중치 초기화
            
            # 픽업 캐릭터 뽑기 시도
            if random.random() < 0.4 or ceil == 4:
                pickup_count += 1
                ceil = 0  # 픽업 천장 초기화
            else:
                ceil += 1  # 픽업 천장 증가
        else:
            weight += 1
    
    return ssr_count, pickup_count

def Until_the_pickup_comes_out(arg):
    pickup = arg[0]
    weight = arg[1]
    goal = arg[2]
    ssr_pulls = 0
    pickup_ceil = pickup
    weight_count = weight
    ssr_probability = 150  # 기본 확률 1.5% (0.015 * 10000)
    ssr_count = 0
    ssr_attempts = 0
    pickup_attempts = 0
    i = 0
    for i in range(1, goal * 250 + 1):
        weight_count += 1
        ssr_attempts += 1
        pickup_attempts += 1
        
        # 확률 가중치 적용
        if weight_count < 30:
            ssr_probability += 1  # 0.01%
        elif weight_count < 40:
            ssr_probability += 30  # 0.3%
        elif weight_count < 50:
            ssr_probability += 100  # 1%
        elif weight_count == 50:
            ssr_probability = 10000  # 100%

        # SSR 뽑기 시도
        if random.random() * 10000 < ssr_probability:
            ssr_pulls += 1
            ssr_count += 1
            ssr_probability = 150
            weight_count = 0

            # 픽업 캐릭터 뽑기 시도
            if random.random() < 0.4 or pickup_ceil == 4:
                goal -= 1
                pickup_ceil = 0
                if not goal:
                    break
            else:
                pickup_ceil += 1

    return ssr_pulls, i

def calculate_percentage(counter, threshold):
    return sum(count for number, count in counter.items() if number >= threshold) / sum(counter.values()) * 100

def quantile(counter, threshold):
    sorted_data = []
    for key in sorted(counter.keys()):
        sorted_data.extend([key] * counter[key])

    return np.percentile(sorted_data, threshold)

if __name__ == "__main__":
    
    simulation_choose= int(input('n회 가챠 = 1, 목표치 달성할 때까지 가챠 = 0: '))
    if simulation_choose:
        trials = int(input('가챠 횟수: '))
    while True:
        goal = int(input('목표 픽업 개수: '))
        if trials//250 <= goal and trials >= goal:
            break
    weight = int(input('가중치: '))
    pickup = int(input('천장횟수: '))
    repeat = int(input('시뮬레이션 횟수: '))
        
    if simulation_choose:
            # 멀티프로세싱 풀 설정
        with Pool() as pool:
            results = pool.map(gacha_n_times, [(trials, pickup, weight) for _ in range(repeat)])
        
        # 결과 수집
        ssr = []
        pick_up = []
        
        for res in results:
            ssr_count, pickup_count = res
            ssr.append(ssr_count)
            pick_up.append(pickup_count)
        
        ssr.sort()
        pick_up.sort()
        a = Counter(pick_up)
        b = Counter(ssr)
        
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(a.keys(), a.values(), color='#ff0080', linestyle='--', marker='h', mfc='#ff008080', ms=10, mec='#ff0080')
        ax2.plot(b.keys(), b.values(), color='#8000ff', linestyle='--', marker='h', mfc='#8000ff80', ms=10, mec='#8000ff')
        a_keys = [i for i in a.keys()]
        a_values = [i for i in a.values()]
        b_keys = [i for i in b.keys()]
        b_values = [i for i in b.values()]
        
        plt.xlabel(f'{trials}회 만에 뽑은 픽업 수')
        plt.ylabel('빈도')
        plt.hlines(0, min(a_keys), max(a_keys), colors='black')
        plt.vlines(goal, 0, a[goal], colors='#ff8000', linestyles='solid', label='목표')
        plt.vlines(sum([i*j for i,j in a.items()])/repeat, 0, max(a_values), colors='#8000ff', linestyles='dotted', label='픽업 기댓값')
        plt.vlines(sum([i*j for i,j in b.items()])/repeat, 0, max(a_values), colors='#0080ff', linestyles='dotted', label='SSR 기댓값')
        ax1.set_ylim(bottom=0)
        ax2.set_ylim(bottom=0)
        # plt.fill_between(keys[keys.index(goal):], values[keys.index(goal):], alpha=0.1, color='#ff0080')

        plt.title(
            f'''가중치: {weight}, 천장횟수: {pickup}, 가챠: {trials}회, {repeat}번 시뮬레이션 결과
            SSR 기댓값: {sum([i*j for i,j in b.items()])/repeat} | 픽업 기댓값: {sum([i*j for i,j in a.items()])/repeat} | {goal}개 이상 뽑을 확률: {calculate_percentage(a, goal):.2f}%
            '''
        )

        for i, j in a.items():
            height = j
            plt.text(i, height + repeat / 500, f'{height}', ha='center', va='bottom', size=12)
        plt.legend()
        plt.show()
    else:
        with Pool() as pool:
            results = pool.map(Until_the_pickup_comes_out, [(pickup, weight, goal) for _ in range(repeat)])
        ssr = 0
        pick_up = []
        
        for res in results:
            ssr_pulls, trial = res
            ssr += ssr_pulls
            pick_up.append(trial)
        pick_up.sort()
        a = Counter(pick_up)
        for i,j in a.items():
            print(i, j)
            
        
        keys = [i for i in a.keys()]
        values = [i for i in a.values()]
        q1 = quantile(a,25)
        q2 = quantile(a,50)
        q3 = quantile(a,75)
        mean = sum([i*j for i,j in a.items()])/repeat
        
        fig, ax = plt.subplots()
        ax.set_facecolor('#404040')
        ax.set_ylim(bottom=0,top=a.most_common(1)[0][1]*1.1)
        plt.xlabel(f'픽업 {goal}개 뽑는데 시도한 횟수')
        plt.ylabel('빈도')
        plt.xticks(np.arange(0, goal*250+1, goal*10))
        plt.plot(a.keys(), a.values(), color='#ffffff', linestyle='-')
        plt.scatter(mean, (a[math.floor(mean)]+a[math.ceil(mean)])/2, color='#ff00ff', marker='h', label = 'mean', zorder=3)
        plt.scatter(a.most_common(1)[0][0], a.most_common(1)[0][1], color='#ffff00', marker='h', label = 'mode', zorder=3)
        plt.scatter(q2, a[q2], color='#00ffff', marker='h', label='median', zorder=3)
        # plt.text(mean, (a[math.floor(mean)]+a[math.ceil(mean)])/2 + a.most_common(1)[0][1]*1.1/100, 'mean', fontsize=10, color='white', ha='center', va='bottom')
        # plt.text(a.most_common(1)[0][0], a.most_common(1)[0][1] + a.most_common(1)[0][1]*1.1/100, 'mode', fontsize=10, color='white', ha='center', va='bottom')
        # plt.text(q2, a[q2] + a.most_common(1)[0][1]*1.1/100, 'median', fontsize=10, color='white', ha='center', va='bottom')
        plt.fill_between(keys[keys.index(q1):keys.index(q3)], values[keys.index(q1):keys.index(q3)], alpha=0.25, color='#ffffff')
        # plt.fill_between(keys[keys.index(quantile(a,2.5)):keys.index(quantile(a,97.5))], values[keys.index(quantile(a,2.5)):keys.index(quantile(a,97.5))], alpha=0.25, color='#ffffff')
        # plt.fill_between(keys[keys.index(quantile(a,0.5)):keys.index(quantile(a,99.5))], values[keys.index(quantile(a,0.5)):keys.index(quantile(a,99.5))], alpha=0.25, color='#ffffff')
        plt.xlim(goal,goal*250)
        plt.title(
            f'''가중치: {weight} | 천장횟수: {pickup} | 목표 픽업개수: {goal}
{repeat}번 시뮬레이션 결과
평균값: {sum([i*j for i,j in a.items()])/repeat}회 | 최빈값: {a.most_common(1)[0][0]}회
제1분위수: {q1}회 | 제2분위수: {q2}회 | 제3분위수: {q3}회'''
        )
        plt.legend()
        plt.show()

def calculate_cumulative_pickup_probability():
    SSR_probability = 150
    weight = 1
    result = []
    for _ in range(1, 251):
        if weight < 30:
            SSR_probability = 150 + weight * 1 # 0.01%
        elif weight < 40:
            SSR_probability = 179 + (weight-30) * 30  # 0.3%
        elif weight < 50:
            SSR_probability = 479 + (weight-40) * 100  # 1%
        elif weight == 50:
            SSR_probability = 10000  # 100%
        
        result.append(SSR_probability)
        if weight == 50:
            weight = 1
        else:
            weight += 1
    return result

# 누적 확률 계산
# pickup_prob_list = calculate_cumulative_pickup_probability()
# new_list = []
# for n in range(len(pickup_prob_list)):
#     product = 1
#     for i in range(n+1):
#         product *= 100000 - pickup_prob_list[i]
#     new_value = product
#     new_list.append(str(new_value))
#     print(n+1, ': ',pickup_prob_list[n]/100,'%', sep='', end=' ')
#     if (i + 1) % 10==0: print('')

# for i,j in enumerate(new_list):
#     if len(j) > (i+1)*5:
#         tmp = j[:len(j)-(i)*5] + '.' + j[len(j)-(i+1)*5:]
#         new_list[i] = tmp.rstrip("0")
#     elif j == 0:
#         new_list[i] = '0'
#     else:
#         tmp = '0' * ((i+1)*5-len(j))
#         tmp = '0.' + str(tmp) + str(j)
#         new_list[i] = tmp.rstrip("0")
#     print(f'{i+1}: {pickup_prob_list[i]/100}%\n {new_list[i]}')